# GOG Galaxy Local Games integration

## ❓What function does this plugin serve? How does it differ from importing games from GOG Galaxy?

Well, it's true that GOG allows you to add games of your choice to the library and link an executable file.

<img width="254" height="239" alt="Captura de pantalla 2026-10-08 171442" src="https://github.com/user-attachments/assets/09cbd9a7-2e24-481d-bb54-37e451c7efa4" />

However, there is a problem with this: it doesn't let you add **ANY** game you want—only those in GOG's database. While it's true that GOG boasts a vast game catalog (unlike emulators), you are still limited if you, as a user, want to add a lesser-known game.

<img width="772" height="233" alt="Captura de pantalla 2026-10-08 172108" src="https://github.com/user-attachments/assets/b159ccd3-f80a-4e57-b492-968b2aa5bf28" />

With this plugin, in addition to being able to link any executable you choose, it can be useful for running multiple instances of a game—for example:

<img width="642" height="627" alt="Captura de pantalla 2026-10-08 174813" src="https://github.com/user-attachments/assets/6847ceaa-7311-4451-bfbe-c324c20c5db9" />

In short, that's it: add the .exe **YOU** want, add as many games as **YOU** want.

## ❓ Frequently Asked Questions (FAQ)

### Q: Why is the bookmark named "Testing purposes"?

**A:** This is due to GOG's limitations regarding plugins from outside its database; GOG assigns that generic name to anything it doesn't "recognize." You can easily change the name to whatever you prefer—just right-click on the bookmark.

<img width="352" height="198" alt="Captura de pantalla 2026-10-08 175742" src="https://github.com/user-attachments/assets/edfe82a7-7ee3-41f5-a904-11789fab57c8" />

## ❗Limitations

The plugin has certain limitations—which are quite annoying—but they are beyond my control because that is simply how GOG works.

If you want to add or remove a game, you unfortunately have to disconnect and reconnect the plugin to access its settings. This won't cause you to lose your playtime data, but you will lose any custom cover art or images you’ve added. As I said, this is something I cannot change, no matter how much I might want to.

There are two "workarounds" for this issue: one on my end and one for the user.

1) From my side as the developer, I plan to implement a system that recursively searches for executables (.exe files) in the paths specified by the user. However, there is a limitation: the plugin won't be able to distinguish between the actual game and other executables. For instance, a game folder might contain both `game.exe` and `uninstall.exe`; it would be difficult to ensure the plugin launches the correct one, though this is something that can be improved.

2) The user can navigate to the directory where plugin settings are stored and manually add (or remove) games. This is the most feasible solution, even if it isn't the most convenient one.


## 📌 Other emulator plugins

| Integration | Status | Achievements | Game Time | Download |
|-------------|--------|--------------|-----------|----------|
| PS2 | ✅ Released | ⚠️ | ✅ | [Download](https://github.com/Notimagination/galaxy-ps2-integration-renew/tree/main) |
| NES | ✅ Released | ⚠️ / ❌ (Mesen don't support) | ✅ | [Download](https://github.com/Notimagination/galaxy-nes-integration) |
| Switch | ✅ Released  | ❌ | ✅ | [Download](https://github.com/Notimagination/galaxy-switch-integration) |
| PSP | ⏳ Planned | ⚠️ | ✅ | Download |
| WII | ⏳ Planned | ⚠️ | ✅ | Download |
| PS3 | ⏳ Planned | ❌ | ✅ | Download |

  > [!NOTE]
  > Some emulators may support achievements through [RetroAchievements](https://retroachievements.org/), provided that GOG decides to integrate with the system. If that ever happens (which I highly doubt), I’ll implement it.

## 📦 Installation Guide

1. Download the `.zip` file from this repository, or you can check the [releases](https://github.com/Notimagination/galaxy-localgames-integration/releases) page for the latest updates.
   
 <img width="923" height="382" alt="Captura de pantalla 2026-10-08 183726" src="https://github.com/user-attachments/assets/87f266f9-ac48-42eb-9839-295c74fafc89" />

2. Extract and move the `LocalGamesPlugin` folder to your GOG Galaxy plugins directory:

   ```
   %localappdata%\GOG.com\Galaxy\plugins\installed
   ```

3. Open **GOG Galaxy**, go to **Settings** > **Integrations**, and look for **Testing purposes**. Click **Connect**.

   <img width="592" height="502" alt="Captura de pantalla 2026-10-08 181803" src="https://github.com/user-attachments/assets/0143a3ff-e2ee-45e5-8f81-3bcebefefc62" />

4. Configure your games paths:

   <img width="695" height="1223" alt="Captura de pantalla 2026-10-08 182341" src="https://github.com/user-attachments/assets/c3f5914e-7c83-4465-ac3b-1955c075186a" />

5. Click the **Save config** button and wait for your games to import.

   <img width="1964" height="899" alt="Captura de pantalla 2026-10-08 182408" src="https://github.com/user-attachments/assets/7cfc958f-2e8c-45d5-a674-c8046b8e5201" />

🎫 **Having problems? Open a ticket on the [Issues](https://github.com/Notimagination/galaxy-ps2-integration-renew/issues) page**.

