import { Inject, Injectable, Logger } from "@nestjs/common";
import igdb from "igdb-api-node";
import * as process from "process";
import { IgdbSyncAuthService } from "./igdb-sync-auth.service";
import * as retry from "async-retry";
import sleep from "../utils/sleep";
import { JwtAuthService } from "../auth/jwt-auth/jwt-auth.service";
import {
    SupertokensConfigInjectionToken,
    TSupertokensConfig,
} from "../auth/config.interface";
import { HttpService } from "@nestjs/axios";
import { lastValueFrom } from "rxjs";
import { Cron, SchedulerRegistry } from "@nestjs/schedule";

const IGDB_SYNC_CRONJOB_NAME = "igdb-sync";

@Injectable()
/**
 * Sync service responsible for fetching and updating entries to GameNode's database.
 * Creates and updates "Game" entities.
 */
export class IgdbSyncService {
    private logger = new Logger(IgdbSyncService.name);
    // IGDB API's limit
    private readonly itemsPerPage = 500;
    // IGDB API's fields
    private readonly igdbSearchFields = [
        "id",
        "name",
        "slug",
        "checksum",
        "aggregated_rating",
        "aggregated_rating_count",
        "status",
        "summary",
        "url",
        "screenshots.*",
        "game_modes.*",
        "expanded_games.id",
        "expanded_games.name",
        "expanded_games.slug",
        "category",
        "genres.*",
        "platforms.*",
        "dlcs.id",
        "dlcs.name",
        "dlcs.slug",
        "expansions.id",
        "expansions.name",
        "expansions.slug",
        "similar_games.id",
        "similar_games.name",
        "similar_games.slug",
        "cover.*",
        "artworks.*",
        "collection.*",
        "alternative_names.*",
        "external_games.*",
        "franchises.*",
        "keywords.*",
        "game_localizations.*",
        "language_supports.*",
        "first_release_date",
    ];

    constructor(
        private schedulerRegistry: SchedulerRegistry,
        private httpService: HttpService,
        private igdbAuthService: IgdbSyncAuthService,
        private jwtAuthService: JwtAuthService,
        @Inject(SupertokensConfigInjectionToken)
        private config: TSupertokensConfig,
    ) {
        this.logger.log("Created IGDB sync service instance");
        this.start();
    }

    /**
     * Builds a IGDB client (trying to refresh the IGDB token if necessary).
     */
    async buildIgdbClient(): Promise<ReturnType<typeof igdb>> {
        const token = await this.igdbAuthService.refreshToken();
        const igdbClient = igdb(process.env.TWITCH_CLIENT_ID, token);
        this.logger.log(
            "Built a fresh IGDB client at " + new Date().toISOString(),
        );

        return igdbClient;
    }

    /**
     * Starts the IGDB sync process.
     * Fetches entries (with fetch()), handles errors with async-retry and sends results with to queue.
     */
    @Cron("0 0 * * *")
    async start(): Promise<void> {
        this.logger.log("Starting IGDB sync at ", new Date().toISOString());
        const syncCronjob = this.schedulerRegistry.getCronJob(
            IGDB_SYNC_CRONJOB_NAME,
        );

        // Stops the cronjob to prevent it from running while we are fetching.
        syncCronjob.stop();

        let hasNextPage = true;
        let currentOffset = 0;
        try {
            while (hasNextPage) {
                this.logger.log(
                    `Fetching results from offset ${currentOffset}`,
                );
                await retry(
                    async () => {
                        const results = await this.fetch(currentOffset);
                        if (results.data.length === 0) {
                            hasNextPage = false;
                            return;
                        }
                        await this.send(results.data);
                        // Sends results to queue.
                        currentOffset += this.itemsPerPage;
                        hasNextPage = results.data.length >= this.itemsPerPage;

                        await sleep(5000);
                    },
                    {
                        retries: 3,
                        onRetry: (err, attempt) => {
                            this.logger.error(
                                `Error while fetching IGDB results:`,
                            );
                            this.logger.error(err);
                            this.logger.error(
                                `Retry attempts: ${attempt} of 3`,
                            );
                        },
                        minTimeout: 10000,
                    },
                );
            }
        } catch (e) {
            this.logger.error(`Error while fetching IGDB results:`);
            this.logger.error(e);
        }
        // Restarts the cronjob.
        syncCronjob.start();
    }

    /**
     * Fetches entries from IGDB.
     * Do not handle errors here, as this is called by start() which already handles errors.
     * @param offset
     */
    private async fetch(offset: number) {
        const igdbClient = await this.buildIgdbClient();
        // Basic search parameters
        const search = igdbClient
            .fields(this.igdbSearchFields)
            .limit(500)
            .offset(offset);

        const results = await search.request("/games");
        return results;
    }

    /**
     * Propagates errors to caller.
     * @param results
     * @private
     */
    private async send(results: any[]) {
        const jwtToken = await this.jwtAuthService.getJwtToken();
        const res = await lastValueFrom(
            this.httpService.post(
                `${this.config.appInfo.apiDomain}/v1/game-queue/sync`,
                {
                    games: results,
                },
                {
                    headers: {
                        Authorization: `Bearer ${jwtToken}`,
                    },
                },
            ),
        );
    }
}
