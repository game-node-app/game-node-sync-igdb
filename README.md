# game-node-sync
This repository holds a collection of different services/scripts that are responsible for fetching data to be used by GameNode systems.

## The reasoning
We have a very big Typescript-based monorepo, which grows by the day, and is responsible for most of our business logic.  
GameNode, by itself, is already a pretty big system. When you add all the external data that is generally expected to be available, for example, How Long to Beat playtimes, Steam, PSN, XLive syncing, etc. 
You start to notice that NestJS's domain-based modularity (while excellent) is not enough.

## The services
This is a list of all services/scripts currently available, with a brief description of their usage.

### IGDB
This is the simplest and most important service in our infrastructure. The GameNode's games, which are the building blocks of every other system, are actually fetched from the Twitch's IGDB API.  
This is a 'simple' Python script that handles authentication and fetching of IGDB entries.  
Currently, the main API is responsible for validating and parsing said data, but we think it's better that we move it here somewhere down the line.


