/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Health
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }
    /**
     * Register
     * @param email
     * @param password
     * @returns any Successful Response
     * @throws ApiError
     */
    public static registerAuthRegisterPost(
        email: string,
        password: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/register',
            query: {
                'email': email,
                'password': password,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create New Key
     * @param name
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createNewKeyApiKeysCreatePost(
        name: string,
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api-keys/create',
            query: {
                'name': name,
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
