
export interface ColumnType {
    column_types: { [key: string]: string };
    preview_data: Record<string, any>[];
  }
  
  export interface ApiResponse {
    data: ColumnType;
    error?: string;
  }