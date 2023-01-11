# EEG Pseudo Device

It is an EEG system from signal generating to signal displaying.

---

- [EEG Pseudo Device](#eeg-pseudo-device)
  - [Components](#components)
  - [Coding Rules](#coding-rules)
    - [Protocol](#protocol)
    - [Format rules](#format-rules)

## Components

Pseudo EEG device: [signal_sender.py](./signal_sender.py),
it works as a recording EEG collector,
it establishes the EEG signal service,
and broadcasts signals to the connected clients.

EEG data center: [data_center.py](./data_center.py),
it connects to the EEG device,
and it receives the EEG signal in real-time.
Moreover, it establishes the data center service.

EEG explorer: [index.html](./web/index.html),
it connects to the data center service,
and it displays the signals in real-time.

## Coding Rules

### Protocol

Commands:

- C is the client device;
- S is the server device.

| Command | Length | Direction | Description                     |
| ------- | ------ | --------- | ------------------------------- |
| start   | 5      | C to S    | Start transaction               |
| stop    | 4      | C to S    | Stop transaction                |
| data    | dep.   | S to C    | Data package of 40 milliseconds |

The data package has the header of 20 bytes length,
it follows the format

b'data' + (n) + (q) + (k) + (x)

| Notion | format | Length in bytes | Description                           |
| ------ | ------ | --------------- | ------------------------------------- |
| 'data' | 8s     | 8               | The command of data package           |
| n      | \>L    | 4               | The count of the package              |
| k      | \>H    | 2               | The bytes length of the encoded array |
| q      | \<d    | 8               | The time stamp of the package         |
| x      | \<i    | k               | The encoded array                     |

### Format rules

The optional first format char indicates byte order, size and alignment:

- @: native order, size & alignment (default)
- =: native order, std. size & alignment
- <: little-endian, std. size & alignment
- \> : big-endian, std. size & alignment
- !: same as >

The remaining chars indicate types of args and must match exactly;
these can be preceded by a decimal repeat count:

- x: pad byte (no data); c:char; b:signed byte; B:unsigned byte;
- ?: \_Bool (requires C99; if not available, char is used instead)
- h:short; H:unsigned short; i:int; I:unsigned int;
- l:long; L:unsigned long; f:float; d:double; e:half-float.

Special cases (preceding decimal count indicates length):

- s:string (array of char); p: pascal string (with count byte).
