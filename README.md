# TicketNet – Simple Ticket Booking System

SE239 Network Programming – Topic 12
Instructor: Dr. Ahmad Sawalmeh

Team: Layan Abdulaziz Albadr, Jana Bader AlFaraj, Bdour Bader AlFaraj,
Aljohara Bin Thunayan, Shaykhah Alkanhal

## How to run (Python 3, no extra libraries)

1. Start the server in one terminal:
   ```
   python server.py
   ```
2. Start each client in its own terminal (open 3 for the Week 8 test):
   ```
   python client.py              # same computer
   python client.py 192.168.1.20 # server on another computer (use its IP)
   ```
3. Each client types a name (login step), then uses the menu.

## Message format (TCP, one line per message)

| Client request | Server reply | Meaning |
|---|---|---|
| `HELLO <name>` | `WELCOME <name>` | Login / join. Must be sent first |
| `VIEW` | `SEATS 1 2 5 ...` | Free seats |
| `BOOK <seat>` | `BOOKED <seat>` or `TAKEN <seat>` | Try to book a seat |
| `MYBOOKING` | `YOURS <seats>` or `NONE` | This client's seats |
| `QUIT` | `BYE` | Disconnect cleanly |
| anything invalid | `ERROR <reason>` | Unknown command, bad seat, not logged in |

The server uses one thread per client and a `threading.Lock` around the
check-and-book step, so two clients can never get the same seat.

## Milestone evidence

### Week 6 – First connection working
- One client connects, sends `HELLO`, receives `WELCOME`, then `VIEW` → `SEATS ...`.
- Screenshot: server terminal + one client terminal.

### Week 8 – Multiple clients + login/join
- Server running with 3 clients connected at the same time
  (server log shows `3 client(s) online`).
- Each client logged in with `HELLO <name>`.
- All 3 clients tried to book seat 5: one got `BOOKED 5`, the other two got `TAKEN 5`.
- Commands sent before logging in get `ERROR please send HELLO <name> first`.
- Screenshot: server terminal + three client terminals side by side.


## Team contributions

- Shaykhah Alkanhal 202400951: Documentation Lead (README, deliverable report)
-Aljohara Bin Thunayan 202401618: Testing & Demo Lead (testing with 3 clients)
