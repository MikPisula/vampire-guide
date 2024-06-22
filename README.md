# vampire-guide

## Development setup

Project dependencies might be installed using [PDM](https://pdm-project.org/en/latest/)
Refer to PDM documentation for:
- [PDM Installation](https://pdm-project.org/en/latest/#installation) 
- [Managing Dependencies](https://pdm-project.org/en/latest/usage/dependency/#manage-dependencies)

TLDR; install PDM then use the command `pdm sync` to install all dependencies.

Also: `pip install -r requirements.txt`

## Notes

Downloading polygons is really slow. Population density of Gdańsk is 712/sqkm, NYC is 96/hectar, so Gdańsk is 13 times less densely populated. A circle of area 20sqkm from which NYC data was downloaded in 5 minutes. Hence in Gdańsk it could be 13 (lets say 10) times faster. So 30 seconds per 20sqkm, and for entire Gdańsk of 260sqkm it would take around a minute.

If it takes a minute for a major Polish City, maybe lets download the whole Poland?
