# Input Folder

Put configuration dumps in the network subfolders:

| Subfolder | When it is searched |
|---|---|
| `input/5G` | 5G ticked in the tool |
| `input/4G` | 4G ticked |
| `input/3G` | 3G ticked |
| `input/2G` | 2G ticked |

- Any file names; more than one file; no file-count limit
- Any number of sheets and columns
- Sheet names that match an MO / MML Object are treated as that object
- 4G `Cell` sheet maps eNodeB + Local Cell ID to L09/L18/L21/L26
- 5G `NRDUCell` sheet maps gNodeB + NR DU Cell ID to the NR band (N41 → L26 family)

Supported: `.xlsx` `.xlsb` `.xlsm`

```bash
./run_audit.sh --rats 4G,5G
```
