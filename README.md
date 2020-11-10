# github_miner

This app allows you to mine github repositories. You can read them from GHArchive.
Save the files in **raw_data** folder. Each record (json like) must be done as follows:
```
{"id": "7044402209", "filename": "2018-01-01-0.json.gz", "sha": "a3d7086eeb885a718225bcf33d4f3e84c419e433", "repo": "AquaFlyRat/ProjectX", "message": "hud update, bug fixes", "author": "bwalter", "api": "https://api.github.com/repos/AquaFlyRat/ProjectX/commits/a3d7086eeb885a718225bcf33d4f3e84c419e433", "created_at": "2018-01-01T00:01:01Z"}
```
The following code is looking for bug fix commits where the number of lines changed is less than 4. You need to **set your github api token** in `miner` function inside `model.py` file.
Please be sure that all the following directories are created in the root folder:
1. **raw_data** where you can insert txt files containing records as show above
2. **result** where are saved the result of bug fixing mining.
3. **output_files** where you can find the code of bug fix files

The **result** folder contains records like the following:
```
{"id_internal": "7044634385", "tot_processed": 799, "id_commit": "50dc9db52e5b062c41e94e404b850c15c42ca468", "repo": "alanlh/No-Click-Click-Game", "date_commit": "2018-01-01 06:01:19", "before_api": "https://github.com/alanlh/No-Click-Click-Game/raw/cdb04bc95fab5881500bd793c3b00f0dd20324e9/app/src/main/java/edu/illinois/finalproject/LeaderboardAdapter.java", "after_api": "https://github.com/alanlh/No-Click-Click-Game/raw/50dc9db52e5b062c41e94e404b850c15c42ca468/app/src/main/java/edu/illinois/finalproject/LeaderboardAdapter.java", "URL": "https://api.github.com/repos/alanlh/No-Click-Click-Game/commits/50dc9db52e5b062c41e94e404b850c15c42ca468", "message": "Started working on UI. Minor bug fixes.", "file_path": "2018-01-01-6.json.gz", "modifications": "3 3"}
```
There are all information about the commit. `id_internal` is the unique id (read from GHArchive).

In **output_files** you can find two files for each record stored in result folder: a before and after version. The *before version* contains the version of the java file before the bug fix commit, the *after version* contains the version with the fix.

To run the code install all required packages (requirements.txt) and then you can run
```
python3 mining.py
```
