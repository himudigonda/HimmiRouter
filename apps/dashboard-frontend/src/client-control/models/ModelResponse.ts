/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CompanyResponse } from './CompanyResponse';
import type { MappingResponse } from './MappingResponse';
export type ModelResponse = {
    id: number;
    name: string;
    slug: string;
    context_length?: (number | null);
    company?: (CompanyResponse | null);
    mappings?: Array<MappingResponse>;
};

