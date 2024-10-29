import axios from 'axios';
import { ApiResponse, ColumnType } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const uploadFile = async (file: File): Promise<ApiResponse> => {
  try {
    
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/process-file/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });


    return { data: response.data };
  } catch (error) {
    
    if (axios.isAxiosError(error)) {
      return { 
        data: {} as ColumnType, 
        error: error.response?.data?.error || 'Error uploading file' 
      };
    }
    return { 
      data: {} as ColumnType, 
      error: 'An unexpected error occurred' 
    };
  }
};

export const updateTypes = async (columnTypes: {[key: string]: string}, previewData: any[]): Promise<ApiResponse> => {
  try {
      const response = await axios.post(`${API_BASE_URL}/update-types/`, {  
          column_types: columnTypes,
          preview_data: previewData
      });

      return { data: response.data };
  } catch (error) {
      if (axios.isAxiosError(error)) {
          return {
              data: {} as ColumnType,
              error: error.response?.data?.error || 'Error updating types'
          };
      }
      return {
          data: {} as ColumnType,
          error: 'An unexpected error occurred'
      };
  }
};