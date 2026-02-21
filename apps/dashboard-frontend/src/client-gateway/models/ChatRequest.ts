/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatMessage } from './ChatMessage';
export type ChatRequest = {
    model: string;
    messages: Array<ChatMessage>;
    stream?: (boolean | null);
    shadow_mode?: (boolean | null);
};

