import { Inject, Injectable, Logger } from "@nestjs/common";
import supertokens from "supertokens-node";
import jwt from "supertokens-node/recipe/jwt";

import {
    SupertokensConfigInjectionToken,
    TSupertokensConfig,
} from "./config.interface";

/**
 * The Auth Service
 * uses SuperTokens to provide authentication
 */
@Injectable()
export class AuthService {
    private logger = new Logger(AuthService.name);

    constructor(
        @Inject(SupertokensConfigInjectionToken)
        private config: TSupertokensConfig,
    ) {
        console.log(this.config.appInfo);
        supertokens.init({
            appInfo: this.config.appInfo,
            supertokens: {
                connectionURI: this.config.connectionURI,
                apiKey: this.config.apiKey,
            },
            recipeList: [jwt.init()],
        });
    }
}
