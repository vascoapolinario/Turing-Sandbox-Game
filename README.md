# Turing Sandbox
A game made with python using pygame to build and simulate turing machines

Latest version (windows) download release at:
- [https://github.com/vascoapolinario/Turing-Sandbox-Game/releases/tag/1.0.1](https://github.com/vascoapolinario/Turing-Sandbox-Game/releases/tag/1.0.1)

If you have PyInstaller you can build the exe yourself by running the following command inside the src folder
`PyInstaller main.py --onefile --noconsole --icon=assets/favicon.ico --add-data "assets/favicon.ico:assets"
`

View the workshop and other game details through the API dashboard available at:
- [https://vapoli.tech/#/TuringSandbox/dashboard](https://vapoli.tech/#/TuringSandbox/dashboard)

Code for the API (Server) available at:
[TuringMachinesAPI](https://github.com/vascoapolinario/TuringMachinesAPI)

# Game Preview
In this game preview you can see a level being solved, the level expects the user to build a turing machine that turns all zeros to ones and ones to zeros

![ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/11a891f0-a6c6-41cf-98c9-0cbe77ee4f06)



# Key Features
## Sandbox Mode
<img width="1906" height="991" alt="image" src="https://github.com/user-attachments/assets/14bdf3cc-3308-4e77-9417-3443724bc2b4" />

- Create Turing Machines freely with no restrictions.

- Edit states, transitions, and tape contents interactively.

- Run, pause, and step through simulations.

## Level Mode
<img width="1833" height="960" alt="image" src="https://github.com/user-attachments/assets/8e96076b-b17d-40ce-9e00-d0a6b33eee9a" />

- Play levels that test your understanding of Turing Machines.

- Each level defines objectives and test cases your solution must satisfy.

- Includes built-in examples and support for user-created levels.

## Multiplayer

![2025-10-2921-09-09-ezgif com-video-to-gif-converter (1)](https://github.com/user-attachments/assets/ef1b8198-961a-43f9-b4a3-66d7a7460198)

- Powered by SignalR and the TuringSandboxAPI, the multiplayer system allows real-time collaboration between players.

- Host and join lobbies directly from the in-game menu. Lobbies are automatically synchronized and updated live as players connect or leave.

- More multiplayer modes and tools like competitively building machines are planned for future release.

## Saving & Loading
<img width="1769" height="965" alt="image" src="https://github.com/user-attachments/assets/1b9bd6b3-a160-475c-b14d-a333fbd5fb77" />


- Machines and levels are stored as JSON files under your Documents folder:

  - ~/Documents/Turing Sandbox Saves/


- Supports automatic saving of workshop downloads and local creations.

- Saved machines can be reopened or shared across devices.

- Level progress is also saved using json

## Workshop
<img width="1877" height="959" alt="image" src="https://github.com/user-attachments/assets/8a6ad383-7a0b-4106-b183-434e5ebec9ad" />


- Browse and download machines or levels created by other users.

- Rate creations or upload your own.

- Requires login (handled through the in-game authentication popup).

## Double Tape Support
<img width="1919" height="982" alt="image" src="https://github.com/user-attachments/assets/92f072ce-ae0b-4e6a-beeb-c43dd81390e8" />

- Advanced levels and sandbox setups can use two tapes for more complex machines.

- Each transition supports independent read/write/move operations per tape.

## Discord Rich Presence
<img width="285" height="123" alt="image" src="https://github.com/user-attachments/assets/5fd33218-18d9-4ff3-aa8d-3a7e7f26cc70" />

- Show that you're playing the game simply by running it, if the game detects you have discord open it will show up as a running activity.

- Discord rich presence shows your status in the game. it can be very easily disabled trough discord.

# Policies
Because the game includes online features such as multiplayer and the community workshop, users can share and upload their own creations.
To keep things safe, fair, and clear for everyone, a few documents outline how content is handled and what’s expected from players.
You can find them in the [`/docs`](docs) folder:

- [Disclaimer](docs/DISCLAIMER.md)
- [Terms of Service](docs/TERMS_OF_SERVICE.md)
- [Privacy Policy](docs/PRIVACY_POLICY.md)
- [Security Policy](docs/SECURITY_POLICY.md)
- [Content Policy](docs/CONTENT_POLICY.md)

These documents exist to protect both players and the project maintainers, and to make sure that if any problems occur (for example, someone uploads disallowed or harmful content), there’s a clear way to handle it responsibly.
If you ever notice an issue, please report it through GitHub Issues or the contact info provided.

