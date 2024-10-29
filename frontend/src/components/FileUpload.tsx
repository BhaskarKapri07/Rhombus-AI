import { useState } from 'react';
import { 
  Group, 
  Text, 
  useMantineTheme, 
  rem,
  Button,
  Alert,
  LoadingOverlay,
  Table,
  Title,
  Select
} from '@mantine/core';
import { Dropzone } from '@mantine/dropzone';
import { IconUpload, IconX, IconFileAnalytics } from '@tabler/icons-react';
import { uploadFile, updateTypes } from '../services/api';
import { ColumnType } from '../types';

const DATA_TYPES = [
  { value: 'Int64', label: 'Integer' },
  { value: 'float64', label: 'Decimal' },
  { value: 'datetime64[ns]', label: 'Date/Time' },
  { value: 'bool', label: 'Boolean' },
  { value: 'category', label: 'Category' },
  { value: 'object', label: 'Text' }
];

const FileUpload = () => {
  const theme = useMantineTheme();
  const [isLoading, setIsLoading] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ColumnType | null>(null);
  const [columnTypes, setColumnTypes] = useState<{[key: string]: string}>({});
  const [hasChanges, setHasChanges] = useState(false);

  const handleFileUpload = async (files: File[]) => {
    const file = files[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await uploadFile(file);
      if (response.error) {
        setError(response.error);
      } else {
        setData(response.data);
        setColumnTypes(response.data.column_types); 
        setHasChanges(false);
      }
    } catch (err) {
      setError('Error uploading file ');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTypeChange = (column: string, newType: string) => {
    setColumnTypes(prev => ({
      ...prev,
      [column]: newType
    }));
    setHasChanges(true);
  };

  const handleApplyChanges = async () => {
    if (!data) return;

    setIsApplying(true);
    setError(null);
    try {
      const response = await updateTypes(columnTypes, data.preview_data);
      if (response.error) {
        setError(response.error);
      } else {
        setData(response.data);
        setHasChanges(false);
        alert('Types updated successfully!');
      }
    } catch (err) {
      setError('Error applying type changes');
    } finally {
      setIsApplying(false);
    }
  };

  const getTypeLabel = (type: string) => {
    return DATA_TYPES.find(t => t.value === type)?.label || type;
  };

  return (
    <div style={{ position: 'relative' }}>
      <LoadingOverlay visible={isLoading || isApplying} overlayProps={{ blur: 2 }} />
      
      <Dropzone
        onDrop={handleFileUpload}
        maxSize={5 * 1024 ** 2}
        accept={[
          'application/vnd.ms-excel',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'text/csv'
        ]}
        multiple={false}
      >
        <Group justify="center" gap="xl" mih={220} style={{ pointerEvents: 'none' }}>
          <Dropzone.Accept>
            <IconUpload
              style={{ width: rem(52), height: rem(52), color: theme.colors.blue[6] }}
              stroke={1.5}
            />
          </Dropzone.Accept>
          <Dropzone.Reject>
            <IconX
              style={{ width: rem(52), height: rem(52), color: theme.colors.red[6] }}
              stroke={1.5}
            />
          </Dropzone.Reject>
          <Dropzone.Idle>
            <IconFileAnalytics
              style={{ width: rem(52), height: rem(52), color: theme.colors.gray[6] }}
              stroke={1.5}
            />
          </Dropzone.Idle>

          <div>
            <Text size="xl" inline>
              Drag CSV or Excel files here or click to select
            </Text>
            <Text size="sm" c="dimmed" inline mt={7}>
              Files should not exceed 5mb
            </Text>
          </div>
        </Group>
      </Dropzone>

      {error && (
        <Alert color="red" title="Error" mt="md">
          {error}
        </Alert>
      )}

      {data && (
        <div style={{ marginTop: '2rem' }}>
          <Group justify="space-between" mb="md">
            <Title order={2}>Column Types</Title>
            <Button 
              onClick={handleApplyChanges}
              disabled={!hasChanges}
              loading={isApplying}
            >
              Apply Changes
            </Button>
          </Group>
          
          <Table striped highlightOnHover withTableBorder>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Column Name</Table.Th>
                <Table.Th>Inferred Type</Table.Th>
                <Table.Th>Override Type</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {Object.entries(columnTypes).map(([column, type]) => (
                <Table.Tr key={column}>
                  <Table.Td>{column}</Table.Td>
                  <Table.Td>{getTypeLabel(type)}</Table.Td>
                  <Table.Td>
                    <Select
                      value={type}
                      onChange={(value) => handleTypeChange(column, value || type)}
                      data={DATA_TYPES}
                      w={200}
                    />
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>

          <Title order={2} mt="xl" mb="md">Data Preview</Title>
          <Table striped highlightOnHover withTableBorder>
            <Table.Thead>
              <Table.Tr>
                {Object.keys(data.preview_data[0] || {}).map((header) => (
                  <Table.Th key={header}>{header}</Table.Th>
                ))}
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.preview_data.map((row, index) => (
                <Table.Tr key={index}>
                  {Object.values(row).map((value, cellIndex) => (
                    <Table.Td key={cellIndex}>
                      {value === null ? 'NULL' : String(value)}
                    </Table.Td>
                  ))}
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default FileUpload;