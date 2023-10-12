import { MiddlewareConsumer, Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import * as process from "process";
import { ScheduleModule } from "@nestjs/schedule";
import { LoggerMiddleware } from "./app.logger.middlewhare";
import { AuthModule } from "./auth/auth.module";
import { redisStore } from "cache-manager-redis-yet";
import { CacheModule } from "@nestjs/cache-manager";
import { SupertokensConfigInjectionToken } from "./auth/config.interface";
import { GlobalModule } from "./global/global.module";
import { IgdbSyncModule } from "./sync/igdb-sync.module";

@Module({
    imports: [
        ScheduleModule.forRoot(),
        GlobalModule,
        CacheModule.registerAsync({
            isGlobal: true,
            useFactory: async () => ({
                store: await redisStore({
                    url: process.env.REDIS_URL,
                }),
            }),
        }),
        AuthModule,
        IgdbSyncModule,
    ],
    providers: [],
})
export class AppModule {
    configure(consumer: MiddlewareConsumer): void {
        consumer.apply(LoggerMiddleware).forRoutes("*");
    }
}
