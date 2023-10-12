import {
    MiddlewareConsumer,
    Module,
    NestModule,
    DynamicModule,
} from "@nestjs/common";

import { AuthMiddleware } from "./auth.middleware";
import { AuthService } from "./auth.service";

@Module({
    providers: [AuthService],
})
export class AuthModule implements NestModule {
    configure(consumer: MiddlewareConsumer) {
        consumer.apply(AuthMiddleware).forRoutes("*");
    }
}
