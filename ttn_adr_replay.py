"""Transmit power of every uplink, replayed from The Things Stack's ADR.

The end-device sketch leaves ADR on (modem.setADR(true)), forces only the data rate before each uplink and never
sets a power, so the network server chose the transmit power of every uplink through LinkADRReq commands, and the
TTN export does not record it. This module replays the server's decisions on the whole export, uplink by uplink,
and returns the power the device used for each row.

Network-server side, as in lorawan-stack at commit e27dcfc90a (April 2024; the code on TTN until v3.34.3 on
14 Oct 2025, which covers the whole campaign):
  grpc_gsns.go  per received uplink: append it to the last 20 uplinks; if its data rate is below the current ADR
                data rate, the current TX power index is reset to 0; the current ADR data rate becomes the uplink's;
                then AdaptDataRate.
  adr.go        ADR uplinks = the trailing uplinks at the current data rate since the last accepted LinkADRAns;
                margin = max SNR over all gateways of those uplinks - demodulation floor(SF of the last) - 15 dB,
                minus 2.5 dB while fewer than 20 uplinks are in the window; adrAdaptDataRate, adrAdaptTxPowerIndex
                and adrAdaptNbTrans as written there (float32 arithmetic).
  link_adr.go   a LinkADRReq is sent when the desired data rate, TX power index or NbTrans differs from the current
                one; an accepted LinkADRAns books the request as current and restarts the ADR window.
Device side: the device applies every LinkADRReq it receives (the power persists; the sketch re-forces only the data
rate) and answers in its next frame; a join resets it to index 0. EU868: index k is 14 - 2k dBm.
Two conventions of the JSON export: an empty f_cnt is frame 0, and an empty SNR of a listed gateway is 0 dB.
Assumed: every downlink after a received uplink reached the device and every request was accepted.

Checks that did not enter the replay (Oct 2026): the SF11 airtime shows the LinkADRAns on 99.77 % of 284,540 SF11
uplinks exactly where the replay expects it; TTN's own packet_error_rate is reproduced on 99.99 % of uplinks; the
gateway's RSSI steps by +2.02 and -1.88 dB at the two SNR thresholds of the rule (+-2 dB predicted); an independent
implementation gives the same power for every uplink.
"""
import numpy as np
import pandas as pd

F32 = np.float32
FLOOR = {7: F32(-7.5), 8: F32(-10), 9: F32(-12.5), 10: F32(-15), 11: F32(-17.5), 12: F32(-20)}  # 125 kHz
TX_OFFSET = [F32(-2 * i) for i in range(8)]  # EU868: index 0..7 = 0 to -14 dB
MAX_TP, MAX_ADR_DR = 7, 5
ADR_MARGIN, SAFETY, DR_STEP = F32(15), F32(2.5), F32(2.5)
OPTIMAL, WINDOW = 20, 20
P = 'uplink_message_'


def loss_rate(fcnts):
    """adrLossRate: lost frames over the FCnt span of the ADR uplinks (restarting after a counter reset)."""
    if len(fcnts) < 2:
        return 0.0
    lo = last = fcnts[0]
    lost = 0
    for i, f in enumerate(fcnts[1:]):
        if f < last:
            return loss_rate(fcnts[1 + i:])
        if f >= last + 1:
            lost += f - last - 1
        last = f
    return float(F32(lost) / F32(1 + last - lo))


def adapt(recent, cur_dr, cur_tp, cur_nb, last_change):
    """AdaptDataRate after the uplink recent[-1]: the desired (data rate, TX power index, NbTrans)."""
    hist = []
    for dr, f, s in reversed(recent):
        if dr != cur_dr or (last_change != 0 and f < last_change):
            break
        hist.append((dr, f, s))
    hist.reverse()
    snrs = [s for _, _, s in hist if not np.isnan(s)]
    if not snrs:
        return cur_dr, cur_tp, cur_nb
    sf_last = 12 - hist[-1][0]
    margin = F32(max(F32(x) for x in snrs)) - FLOOR[sf_last] - ADR_MARGIN
    optimal = len(hist) >= OPTIMAL
    if not optimal:
        margin = F32(margin - SAFETY)
    # adrAdaptDataRate (min DR index 0, max 5, every DR allowed, min TX power index 0)
    d_dr, d_tp = cur_dr, cur_tp
    max_dr = MAX_ADR_DR
    max_steps = F32(max_dr - d_dr)
    steps = F32((margin - F32(0)) / DR_STEP)
    skip = False
    if F32(0) < steps < max_steps:
        max_dr = d_dr + int(steps)
    elif steps <= 0:
        skip = True
    if not skip and max_dr > d_dr:
        margin = F32(margin - F32(max_dr - d_dr) * DR_STEP)
        d_dr, d_tp = max_dr, 0
    # adrAdaptTxPowerIndex (min 0, max 7, nothing rejected)
    for idx in range(MAX_TP, -1, -1):
        diff = F32(TX_OFFSET[d_tp] - TX_OFFSET[idx])
        if diff > margin and idx != 0:
            continue
        if not optimal and diff < 0 and -diff <= SAFETY:
            break
        margin = F32(margin - diff)
        d_tp = idx
        break
    # adrAdaptNbTrans (no NbTrans settings: the clamp is the identity)
    nb = cur_nb
    if len(hist) >= OPTIMAL // 2:
        lr = loss_rate([f for _, f, _ in hist])
        if lr < 0.05:
            nb = 1 + nb // 3
        elif lr < 0.10:
            pass
        elif lr < 0.30:
            nb = 2 + nb // 2
        else:
            nb = 3
    return d_dr, d_tp, nb


def replay_session(dr, f_cnt, max_snr):
    """TX power index of each uplink of one session, given its uplinks in frame-counter order."""
    cur_dr, cur_tp, cur_nb, last_change = 0, 0, 1, 0  # the server's MAC state after the join
    dev_tp = 0                                        # the device's power index after the join
    recent, pending, f_prev = [], None, None
    index = np.zeros(len(dr), dtype=np.int16)
    for i in range(len(dr)):
        d, f, s = int(dr[i]), int(f_cnt[i]), float(max_snr[i])
        if pending is not None:
            dev_tp = pending[1]                       # the device applied the request on the downlink
            if f == f_prev + 1:                       # its answer rides in the next frame, received here
                cur_dr, cur_tp = pending[0], pending[1]
                if pending[2] > 0 and cur_nb != pending[2]:
                    cur_nb = pending[2]
                last_change = f
        index[i] = dev_tp
        recent.append((d, f, s))
        if len(recent) > WINDOW:
            recent = recent[-WINDOW:]
        if d < cur_dr:
            cur_tp = 0
        cur_dr = d
        desired = adapt(recent, cur_dr, cur_tp, cur_nb, last_change)
        pending = desired if desired != (cur_dr, cur_tp, cur_nb) else None
        f_prev = f
    return index


def tx_power_per_row(df):
    """Transmit power in dBm of every row of the raw TTN export (one row per received uplink, duplicates included)."""
    cols = {'end_device_ids_device_id': 'device', f'{P}session_key_id': 'session', f'{P}f_cnt': 'f_cnt',
            f'{P}received_at': 'received_at', f'{P}settings_data_rate_lora_spreading_factor': 'sf'}
    up = df[list(cols)].rename(columns=cols)
    assert up['session'].notna().all(), 'an uplink without a session key'
    up['f_cnt'] = up['f_cnt'].fillna(0).astype(np.int64)  # frame 0 (the first after a join) is exported empty
    up['received_at'] = pd.to_datetime(up['received_at'], utc=True, format='ISO8601')
    up['dr'] = (12 - up['sf']).astype(int)
    # the best SNR over the gateways that received the uplink; TTS omits an SNR of exactly 0 from the export
    snr = [df[f'{P}rx_metadata_{k}_snr'].where(df[f'{P}rx_metadata_{k}_gateway_ids_gateway_id'].isna(),
                                                df[f'{P}rx_metadata_{k}_snr'].fillna(0.0)) for k in range(4)]
    up['max_snr'] = pd.concat(snr, axis=1).max(axis=1)
    key = ['device', 'session', 'f_cnt']
    uplinks = up.drop_duplicates(key + ['received_at'])  # the same uplink ingested twice
    assert not uplinks.duplicated(key).any()
    first = uplinks.groupby(['device', 'session'])['received_at'].transform('min')
    uplinks = uplinks.assign(first=first).sort_values(['device', 'first', 'f_cnt'], kind='mergesort')
    parts = [pd.Series(replay_session(g['dr'].to_numpy(), g['f_cnt'].to_numpy(), g['max_snr'].to_numpy()), index=g.index)
             for _, g in uplinks.groupby(['device', 'session'], sort=False)]
    uplinks['tx_power'] = 14 - 2 * pd.concat(parts)
    power = uplinks.set_index(key)['tx_power'].reindex(pd.MultiIndex.from_frame(up[key]))
    assert power.notna().all()
    return pd.Series(power.to_numpy().astype(np.int64), index=df.index, name='tx_power')
