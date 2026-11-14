"""
TicketNet server - SE239 Network Programming
Simple Ticket Booking System (Topic 12)


One event, a fixed number of seats. Each client gets its own thread.
A single lock protects the seat table so a seat is never booked twice.

Protocol: text over TCP, one message per line, (ends wioth "\n").
    Hello <name>   -> WELCOME <name>        (login / join step, must come first)
    VIEW           -> SEATS 1 2 5 7 ...     (free seats)
    BOOk <seat>    -> BOOKED <seat> | TAKEN <seat>
    MYBOOKING      -> YOURS <seats> | NONE
    QUIT           -> BYE
    anything else  -> ERROR <reason>
"""

import socket
import threading

HOST = "0.0.0.0"
PORT = 5050
TOTAL_SEATS = 20

# seat number -> client name (None means free)
seats = {n: None for n in range(1, TOTAL_SEATS + 1)}
seats_lock = threading.Lock()

# names of clients currently connected (for the server log)
online = set()
online_lock = threading.Lock()
print_lock = threading.Lock()


def log(text):
    with print_lock:
        print(f"[SERVER] {text}", flush=True)


def handle_command(line, name):
    """Process one request line. Returns (reply, new_name, should_close)."""
    parts = line.strip().split()
    if not parts:
        return "ERROR empty message", name, False

    cmd = parts[0].upper()
    args = parts[1:]
#Each client runs in its own thread. the seats_lock makes 
#sure the check and book step happens as one step, so two clients can never book the same seats.
    # --- login / join step ---
    if cmd == "HELLO":
        if name is not None:
            return "ERROR already logged in", name, False
        if len(args) != 1:
            return "ERROR usage: HELLO <name>", name, False
        new_name = args[0]
        with online_lock:
            if new_name in online:
                return "ERROR name already in use", name, False
            online.add(new_name)
            count = len(online)
        log(f"{new_name} joined ({count} client(s) online)")
        return f"WELCOME {new_name}", new_name, False

    if cmd == "QUIT":
        return "BYE", name, True

    # every other command needs a login first
    if name is None:
        return "ERROR please send HELLO <name> first", name, False

    if cmd == "VIEW":
        with seats_lock:
            free = [str(n) for n, owner in seats.items() if owner is None]
        return "SEATS " + " ".join(free) if free else "SEATS NONE", name, False

    if cmd == "BOOK":
        if len(args) != 1 or not args[0].isdigit():
            return "ERROR usage: BOOK <seat number>", name, False
        seat = int(args[0])
        if seat not in seats:
            return f"ERROR seat must be between 1 and {TOTAL_SEATS}", name, False
        # check-and-book must happen inside the lock
        with seats_lock:
            if seats[seat] is None:
                seats[seat] = name
                result = f"BOOKED {seat}"
            else:
                result = f"TAKEN {seat}"
        log(f"{name} BOOK {seat} -> {result.split()[0]}")
        return result, name, False

    if cmd == "MYBOOKING":
        with seats_lock:
            mine = [str(n) for n, owner in seats.items() if owner == name]
        return ("YOURS " + " ".join(mine)) if mine else "NONE", name, False

    return "ERROR unknown command", name, False


def client_thread(conn, addr):
    log(f"new connection from {addr[0]}:{addr[1]}")
    name = None
    reader = conn.makefile("r", encoding="utf-8", newline="\n")
    try:
        for line in reader:
            reply, name, close = handle_command(line, name)
            conn.sendall((reply + "\n").encode("utf-8"))
            if close:
                break
    except (ConnectionResetError, BrokenPipeError):
        pass  # client vanished; just clean up below
    finally:
        if name is not None:
            with online_lock:
                online.discard(name)
                count = len(online)
            log(f"{name} left ({count} client(s) online)")
        else:
            log(f"{addr[0]}:{addr[1]} disconnected")
        reader.close()
        conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    log(f"TicketNet server listening on port {PORT} with {TOTAL_SEATS} seats")
    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        log("shutting down")
    finally:
        server.close()


if __name__ == "__main__":
    main()
