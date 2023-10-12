import { AppInfo } from "supertokens-node/types";

export const SupertokensConfigInjectionToken = "ConfigInjectionToken";

export type TSupertokensConfig = {
    appInfo: AppInfo;
    connectionURI: string;
    apiKey?: string;
};
