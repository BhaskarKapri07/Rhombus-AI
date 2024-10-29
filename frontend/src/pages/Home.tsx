import { Container, Title, Paper } from '@mantine/core';
import FileUpload from '../components/FileUpload';

const Home = () => {
  return (
    <Container size="lg" py="xl">
      <Title order={1} mb="lg" ta="center">
        Data Type Inference Tool
      </Title>
      <Paper shadow="sm" radius="md" p="xl">
        <FileUpload />
      </Paper>
    </Container>
  );
};

export default Home;