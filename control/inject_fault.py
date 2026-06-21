import sys
from control.fault_control import write_fault

COMMANDS = {"overload": "overload", "short": "short_circuit", "clear": None}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python -m control.inject_fault <{'|'.join(COMMANDS)}>")
        sys.exit(1)
    write_fault(COMMANDS[sys.argv[1]])
    print(f"Fault command sent: {sys.argv[1]}")


if __name__ == "__main__":
    main()
