/**
 * Type Definitions
 * 
 * Contains TypeScript interfaces and types used throughout the application.
 * 
 * @module Types
 */


/**
 * Represents the structure of column types and preview data
 */
export interface ColumnType {
    column_types: { [key: string]: string };
    preview_data: Record<string, any>[];
  }
  
/**
 * Represents an API response
 */ 
export interface ApiResponse {
  data: ColumnType;
  error?: string;
}