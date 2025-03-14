import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Grid,
  GridItem,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Avatar,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  useToast
} from '@chakra-ui/react';
import { ChevronDownIcon, HamburgerIcon } from '@chakra-ui/icons';

// Mock data for development
const mockSummaries = [
  {
    id: 1,
    group: { id: 1, name: 'Crypto Enthusiasts', username: 'crypto_talk' },
    start_date: '2025-03-07T00:00:00Z',
    end_date: '2025-03-14T00:00:00Z',
    content: 'This week, the group discussed the recent Bitcoin price movements, with most members expressing optimism about the upcoming halving event. Several new DeFi projects were shared and analyzed. There was a heated debate about the environmental impact of mining, with no clear consensus reached. The group admin announced a virtual meetup scheduled for next month.',
    created_at: '2025-03-14T06:00:00Z'
  },
  {
    id: 2,
    group: { id: 2, name: 'AI Research', username: 'ai_research' },
    start_date: '2025-03-07T00:00:00Z',
    end_date: '2025-03-14T00:00:00Z',
    content: 'The group shared several new papers on large language models this week. There was significant discussion about the latest Gemini 2.0 release and its capabilities compared to GPT-5. Members shared experiences with fine-tuning smaller models for specific domains. A collaborative project was proposed to create a benchmark for evaluating AI agents, with five members volunteering to participate.',
    created_at: '2025-03-14T07:30:00Z'
  },
  {
    id: 3,
    group: { id: 3, name: 'Web Development', username: 'webdev_community' },
    start_date: '2025-03-07T00:00:00Z',
    end_date: '2025-03-14T00:00:00Z',
    content: 'This week focused on the new features in React 19. Several members shared migration guides and experiences. There was a discussion about the state of CSS frameworks, with Tailwind remaining the most popular among members. A few job opportunities were shared for remote positions. The weekly code challenge was about implementing a custom hook for form validation, with three members sharing their solutions.',
    created_at: '2025-03-14T08:15:00Z'
  }
];

const mockAccounts = [
  {
    id: 1,
    phone_number: '+1234567890',
    is_active: true,
    created_at: '2025-02-15T10:00:00Z'
  },
  {
    id: 2,
    phone_number: '+9876543210',
    is_active: false,
    created_at: '2025-03-01T14:30:00Z'
  }
];

const mockGroups = [
  {
    id: 1,
    name: 'Crypto Enthusiasts',
    username: 'crypto_talk',
    is_active: true
  },
  {
    id: 2,
    name: 'AI Research',
    username: 'ai_research',
    is_active: true
  },
  {
    id: 3,
    name: 'Web Development',
    username: 'webdev_community',
    is_active: true
  }
];

export default function Dashboard() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [summaries, setSummaries] = useState(mockSummaries);
  const [accounts, setAccounts] = useState(mockAccounts);
  const [groups, setGroups] = useState(mockGroups);
  const [selectedSummary, setSelectedSummary] = useState(null);
  const toast = useToast();

  // In a real implementation, this would fetch data from the backend API
  useEffect(() => {
    // Fetch summaries, accounts, and groups
  }, []);

  const handleLogout = () => {
    // Logout logic
    toast({
      title: 'Logged out',
      description: "You've been logged out successfully",
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
    // Redirect to login page
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <Box minH="100vh" bg="gray.50">
      {/* Header */}
      <Flex
        as="header"
        align="center"
        justify="space-between"
        py={4}
        px={8}
        bg="white"
        borderBottomWidth="1px"
        borderColor="gray.200"
        boxShadow="sm"
      >
        <HStack spacing={8}>
          <Heading size="md" color="blue.600">Telegram AI Agent</Heading>
          <Button variant="ghost" onClick={onOpen}>
            <HamburgerIcon mr={2} />
            Menu
          </Button>
        </HStack>
        
        <HStack spacing={4}>
          <Menu>
            <MenuButton
              as={Button}
              rightIcon={<ChevronDownIcon />}
              variant="ghost"
            >
              <HStack>
                <Avatar size="sm" name="User" bg="blue.500" />
                <Text>John Doe</Text>
              </HStack>
            </MenuButton>
            <MenuList>
              <MenuItem>Profile</MenuItem>
              <MenuItem>Settings</MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </MenuList>
          </Menu>
        </HStack>
      </Flex>

      {/* Sidebar Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">Navigation</DrawerHeader>
          <DrawerBody>
            <VStack align="stretch" spacing={4} mt={4}>
              <Button variant="ghost" justifyContent="flex-start" leftIcon={<span>📊</span>}>
                Dashboard
              </Button>
              <Button variant="ghost" justifyContent="flex-start" leftIcon={<span>📱</span>}>
                Telegram Accounts
              </Button>
              <Button variant="ghost" justifyContent="flex-start" leftIcon={<span>👥</span>}>
                Groups
              </Button>
              <Button variant="ghost" justifyContent="flex-start" leftIcon={<span>📝</span>}>
                Summaries
              </Button>
              <Button variant="ghost" justifyContent="flex-start" leftIcon={<span>⚙️</span>}>
                Settings
              </Button>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Content */}
      <Box as="main" p={8}>
        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>Summaries</Tab>
            <Tab>Accounts</Tab>
            <Tab>Groups</Tab>
          </TabList>

          <TabPanels>
            {/* Summaries Tab */}
            <TabPanel>
              <VStack align="stretch" spacing={6}>
                <Flex justify="space-between" align="center">
                  <Heading size="lg">Weekly Summaries</Heading>
                  <Button colorScheme="blue">Generate New Summary</Button>
                </Flex>

                {summaries.map((summary) => (
                  <Box 
                    key={summary.id} 
                    p={5} 
                    shadow="md" 
                    borderWidth="1px" 
                    borderRadius="md" 
                    bg="white"
                    _hover={{ shadow: "lg", borderColor: "blue.200" }}
                    onClick={() => setSelectedSummary(summary)}
                    cursor="pointer"
                  >
                    <Flex justify="space-between" align="center" mb={2}>
                      <Heading size="md">{summary.group.name}</Heading>
                      <Badge colorScheme="blue">
                        {formatDate(summary.start_date)} - {formatDate(summary.end_date)}
                      </Badge>
                    </Flex>
                    <Text noOfLines={3}>{summary.content}</Text>
                    <HStack mt={4} justify="space-between">
                      <Text fontSize="sm" color="gray.500">
                        Generated on {formatDate(summary.created_at)}
                      </Text>
                      <Button size="sm" colorScheme="blue" variant="outline">
                        View Full Summary
                      </Button>
                    </HStack>
                  </Box>
                ))}
              </VStack>
            </TabPanel>

            {/* Accounts Tab */}
            <TabPanel>
              <VStack align="stretch" spacing={6}>
                <Flex justify="space-between" align="center">
                  <Heading size="lg">Telegram Accounts</Heading>
                  <Button colorScheme="blue">Add New Account</Button>
                </Flex>

                <Grid templateColumns="repeat(3, 1fr)" gap={6}>
                  {accounts.map((account) => (
                    <GridItem key={account.id}>
                      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg="white">
                        <Flex justify="space-between" align="center" mb={2}>
                          <Heading size="md">{account.phone_number}</Heading>
                          <Badge colorScheme={account.is_active ? "green" : "red"}>
                            {account.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </Flex>
                        <Text fontSize="sm" color="gray.500">
                          Added on {formatDate(account.created_at)}
                        </Text>
                        <HStack mt={4} spacing={2}>
                          <Button size="sm" colorScheme="blue" variant="outline">
                            Manage
                          </Button>
                          <Button size="sm" colorScheme={account.is_active ? "red" : "green"} variant="outline">
                            {account.is_active ? "Deactivate" : "Activate"}
                          </Button>
                        </HStack>
                      </Box>
                    </GridItem>
                  ))}
                </Grid>
              </VStack>
            </TabPanel>

            {/* Groups Tab */}
            <TabPanel>
              <VStack align="stretch" spacing={6}>
                <Flex justify="space-between" align="center">
                  <Heading size="lg">Telegram Groups</Heading>
                  <Button colorScheme="blue">Join New Group</Button>
                </Flex>

                <Grid templateColumns="repeat(3, 1fr)" gap={6}>
                  {groups.map((group) => (
                    <GridItem key={group.id}>
                      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg="white">
                        <Flex justify="space-between" align="center" mb={2}>
                          <Heading size="md">{group.name}</Heading>
                          <Badge colorScheme={group.is_active ? "green" : "red"}>
                            {group.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </Flex>
                        <Text fontSize="sm" color="gray.500">
                          @{group.username}
                        </Text>
                        <HStack mt={4} spacing={2}>
                          <Button size="sm" colorScheme="blue" variant="outline">
                            View Messages
                          </Button>
                          <Button size="sm" colorScheme="blue" variant="outline">
                            Generate Summary
                          </Button>
                        </HStack>
                      </Box>
                    </GridItem>
                  ))}
                </Grid>
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </Box>
  );
}
