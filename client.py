"""
TicketNet client - SE239 Network Programming


Connects to the TicketNet server, logs in with HELLO <name>,
then shows a simple menu. The client keeps no seat data itself;
it only sends requests and prints the server's replies.

Usage:  python client.py [server_ip] [port]
"""

import socket
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5050


def send(sock, reader, message):
    """Send one line and return the server's one-line reply."""
    sock.sendall((message + "\n").encode("utf-8"))
    reply = reader.readline()
    if not reply:
        raise ConnectionError("server closed the connection")
    return reply.strip()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except OSError as e:
        print(f"Could not connect to {HOST}:{PORT} ({e})")
        return
    reader = sock.makefile("r", encoding="utf-8", newline="\n")
    print(f"Connected to TicketNet server at {HOST}:{PORT}")

    # login / join step
    while True:
        name = input("Enter your name (no spaces): ").strip()
        if not name or " " in name:
            print("Name must be one word.")
            continue
        reply = send(sock, reader, f"HELLO {name}")
        print("Server:", reply)
        if reply.startswith("WELCOME"):
            break

    menu = (
        "\n1) View free seats\n"
        "2) Book a seat\n"
        "3) View my booking\n"
        "4) Quit"
    )
    try:
        while True:
            print(menu)
            choice = input("Choose: ").strip()
            if choice == "1":
                print("Server:", send(sock, reader, "VIEW"))
            elif choice == "2":
                seat = input("Seat number: ").strip()
                print("Server:", send(sock, reader, f"BOOK {seat}"))
            elif choice == "3":
                print("Server:", send(sock, reader, "MYBOOKING"))
            elif choice == "4":
                print("Server:", send(sock, reader, "QUIT"))
                break
            else:
                print("Please choose 1-4.")
    except (ConnectionError, OSError) as e:
        print("Connection lost:", e)
    finally:
        reader.close()
        sock.close()


if __name__ == "__main__":
    main()
