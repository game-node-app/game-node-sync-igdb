import { Module } from "@nestjs/common";
import { IgdbSyncService } from "./igdb-sync.service";
import { IgdbSyncAuthService } from "./igdb-sync-auth.service";
import { HttpModule } from "@nestjs/axios";
import { JwtAuthModule } from "../auth/jwt-auth/jwt-auth.module";

@Module({
    imports: [HttpModule, JwtAuthModule],
    providers: [IgdbSyncService, IgdbSyncAuthService],
})
export class IgdbSyncModule {}
