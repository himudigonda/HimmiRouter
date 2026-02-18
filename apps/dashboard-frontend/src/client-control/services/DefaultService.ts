/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuthRequest } from '../models/AuthRequest';
import type { ModelResponse } from '../models/ModelResponse';
import type { ProviderKeyRequest } from '../models/ProviderKeyRequest';
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
     * Login
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static loginAuthLoginPost(
        requestBody: AuthRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Register
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static registerAuthRegisterPost(
        requestBody: AuthRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/register',
            body: requestBody,
            mediaType: 'application/json',
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
    /**
     * List Api Keys
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listApiKeysApiKeysGet(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api-keys',
            query: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Models
     * @returns ModelResponse Successful Response
     * @throws ApiError
     */
    public static listModelsModelsGet(): CancelablePromise<Array<ModelResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/models',
        });
    }
    /**
     * Get User Status
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getUserStatusUsersUserIdGet(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Provider Key
     * @param userId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static addProviderKeyUsersUserIdProviderKeysPost(
        userId: number,
        requestBody: ProviderKeyRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/users/{user_id}/provider-keys',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Provider Keys
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listProviderKeysUsersUserIdProviderKeysGet(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/{user_id}/provider-keys',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Provider Key
     * @param userId
     * @param providerName
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteProviderKeyUsersUserIdProviderKeysProviderNameDelete(
        userId: number,
        providerName: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/users/{user_id}/provider-keys/{provider_name}',
            path: {
                'user_id': userId,
                'provider_name': providerName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
