import React, { useState } from 'react';
import {
  Box,
  Flex,
  Heading,
  Button,
  FormControl,
  FormLabel,
  Input,
  Stack,
  Text,
  useToast,
  Container,
  Image,
  VStack,
  HStack,
  Divider
} from '@chakra-ui/react';

export default function Home() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // This is a placeholder for actual authentication logic
    // In a real implementation, this would connect to the backend API
    try {
      if (isLogin) {
        // Login logic
        toast({
          title: 'Login Successful',
          description: "You've been logged in successfully",
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      } else {
        // Register logic
        toast({
          title: 'Registration Successful',
          description: "Your account has been created",
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || "An error occurred",
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Container maxW="container.xl" p={0}>
      <Flex h={{ base: 'auto', md: '100vh' }} py={[0, 10, 20]} direction={{ base: 'column-reverse', md: 'row' }}>
        {/* Left side - Authentication Form */}
        <VStack w={{ base: 'full', md: '50%' }} h="full" p={10} spacing={10} alignItems="flex-start">
          <VStack spacing={3} alignItems="flex-start">
            <Heading size="2xl">Telegram AI Agent</Heading>
            <Text>Your intelligent assistant for Telegram group summaries</Text>
          </VStack>
          
          <Box as="form" onSubmit={handleSubmit} w="full">
            <Stack spacing={4}>
              {!isLogin && (
                <FormControl id="email">
                  <FormLabel>Email</FormLabel>
                  <Input 
                    type="email" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </FormControl>
              )}
              
              <FormControl id="username">
                <FormLabel>Username</FormLabel>
                <Input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </FormControl>
              
              <FormControl id="password">
                <FormLabel>Password</FormLabel>
                <Input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </FormControl>
              
              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                fontSize="md"
                w="full"
              >
                {isLogin ? 'Sign In' : 'Sign Up'}
              </Button>
            </Stack>
          </Box>
          
          <HStack w="full" justify="center">
            <Text>
              {isLogin ? "Don't have an account?" : "Already have an account?"}
            </Text>
            <Button
              variant="link"
              colorScheme="blue"
              onClick={() => setIsLogin(!isLogin)}
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </Button>
          </HStack>
        </VStack>
        
        {/* Right side - Image/Info */}
        <VStack
          w={{ base: 'full', md: '50%' }}
          h="full"
          p={10}
          spacing={10}
          bg="blue.50"
          alignItems="center"
          justifyContent="center"
        >
          <Box boxSize="sm">
            <Image
              src="https://via.placeholder.com/400x400?text=Telegram+AI+Agent"
              alt="Telegram AI Agent"
              borderRadius="md"
              boxShadow="lg"
            />
          </Box>
          
          <VStack spacing={4} alignItems="center">
            <Heading size="md">Key Features</Heading>
            <Divider />
            <HStack spacing={8}>
              <VStack>
                <Heading size="sm">Telegram Integration</Heading>
                <Text textAlign="center">Connect to Telegram groups as a real user</Text>
              </VStack>
              <VStack>
                <Heading size="sm">AI Summarization</Heading>
                <Text textAlign="center">Weekly summaries powered by Gemini 2.0</Text>
              </VStack>
              <VStack>
                <Heading size="sm">Easy Management</Heading>
                <Text textAlign="center">Control your agents from a single dashboard</Text>
              </VStack>
            </HStack>
          </VStack>
        </VStack>
      </Flex>
    </Container>
  );
}
