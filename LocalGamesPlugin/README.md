# Local Games Integration for GOG Galaxy

Add your own games (any `.exe`) to GOG Galaxy. You choose the name and the executable; the plugin shows the games in Galaxy, launches them and counts your playtime. Nothing is looked up online.

## Install
Copy the `LocalGamesPlugin` folder to `%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\`, restart GOG Galaxy and connect **Local Games** in *Settings → Integrations*.

## Use
- Open the plugin's settings page, press **Add a game**, and fill in the name and the path of the `.exe` (arguments and start folder are optional).
- Hold Shift, right-click the `.exe` in Windows Explorer and choose **Copy as path** to get the path quickly.
- Game names are limited to 30 characters.
- Playtime is counted while the process the plugin started is running. Games that open through another launcher and close the first process right away cannot be timed.

## Data
Everything is stored in `%LOCALAPPDATA%\GOG.com\Galaxy\Configuration\plugins\localgames\` (`library.json`, `game_times.json`). Renaming a game keeps its playtime.

## License
See `LICENSE.md`.
