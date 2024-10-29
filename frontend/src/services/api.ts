/**
 * API Service Module
 * 
 * Handles all API communication between frontend and backend.
 * Includes functions for file upload and data type updates.
 * 
 * @module Services
 */


import axios from 'axios';
import { ApiResponse, ColumnType } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Uploads and processes a file for data type inference
 * 
 * @param file - File to upload (CSV or Excel)
 * @returns Promise with the API response containing inferred types and preview data
 * @throws Error if file upload or processing fails
 */
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


/**
 * Updates data types for specified columns
 * 
 * @param columnTypes - Object mapping column names to their new types
 * @param previewData - Current preview data to update
 * @returns Promise with the API response containing updated types and preview data
 * @throws Error if type update fails
 */
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