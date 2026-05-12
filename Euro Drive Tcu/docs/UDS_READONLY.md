# Read-Only UDS Workflow

This project supports safe UDS diagnostics for confirming that a CAN/J2534 path can reach the TCU.

## Handshake

Request:

```text
CAN TX: configurable, default 0x7E1
CAN RX: configurable, default 0x7E9
Payload: 02 10 03 00 00 00 00 00
Meaning: DiagnosticSessionControl, extended diagnostic session
```

Positive response:

```text
Payload begins with: 02 50 03
```

## ReadDataByIdentifier

Configured DID requests:

```text
03 22 19 01 00 00 00 00
03 22 19 02 00 00 00 00
03 22 19 05 00 00 00 00
```

Positive DID response shape:

```text
05 62 19 01 XX YY 00 00
```

The decoder currently treats the first two data bytes as a big-endian unsigned integer. Scaling comes from `configs/dq500_readonly.yaml`.

## Blocked Services

The code blocks these services:

- `0x27` SecurityAccess
- `0x2E` WriteDataByIdentifier
- `0x34` RequestDownload
- `0x36` TransferData
- `0x37` RequestTransferExit

Use authorized OEM/vendor tooling for protected programming.
