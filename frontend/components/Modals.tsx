import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  useToast,
  Text,
  Heading,
  Divider
} from '@chakra-ui/react';

export const AddAccountModal = ({ isOpen, onClose, onAddAccount }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [apiId, setApiId] = useState('');
  const [apiHash, setApiHash] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [step, setStep] = useState(1);
  const [requestId, setRequestId] = useState(null);
  const toast = useToast();

  const handleSubmitCredentials = async () => {
    // This would connect to the backend API in a real implementation
    try {
      // Mock API call
      // const response = await fetch('/api/telegram/accounts/authenticate', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ phone_number: phoneNumber, api_id: apiId, api_hash: apiHash })
      // });
      // const data = await response.json();
      // setRequestId(data.request_id);
      
      // Mock response
      setRequestId('mock-request-id');
      
      toast({
        title: 'Verification code sent',
        description: 'Please check your Telegram app for the verification code',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
      
      setStep(2);
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to send verification code',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleVerifyCode = async () => {
    // This would connect to the backend API in a real implementation
    try {
      // Mock API call
      // const response = await fetch('/api/telegram/accounts/verify_code', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ 
      //     code: verificationCode, 
      //     request_id: requestId 
      //   })
      // });
      // const data = await response.json();
      
      // Mock response
      const mockAccount = {
        id: Math.floor(Math.random() * 1000),
        phone_number: phoneNumber,
        api_id: apiId,
        api_hash: apiHash,
        is_active: true,
        created_at: new Date().toISOString()
      };
      
      toast({
        title: 'Account added successfully',
        description: 'Your Telegram account has been connected',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      onAddAccount(mockAccount);
      handleReset();
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to verify code',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleReset = () => {
    setPhoneNumber('');
    setApiId('');
    setApiHash('');
    setVerificationCode('');
    setStep(1);
    setRequestId(null);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add Telegram Account</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {step === 1 ? (
            <VStack spacing={4}>
              <Text>
                To connect your Telegram account, you'll need to provide your phone number and API credentials.
              </Text>
              
              <Divider />
              
              <Heading size="sm" alignSelf="flex-start">
                How to get API credentials:
              </Heading>
              <VStack spacing={2} alignItems="flex-start">
                <Text fontSize="sm">1. Visit <a href="https://my.telegram.org/apps" target="_blank" rel="noopener noreferrer">https://my.telegram.org/apps</a></Text>
                <Text fontSize="sm">2. Log in with your phone number</Text>
                <Text fontSize="sm">3. Create a new application if you don't have one</Text>
                <Text fontSize="sm">4. Copy the API ID and API Hash</Text>
              </VStack>
              
              <Divider />
              
              <FormControl isRequired>
                <FormLabel>Phone Number (with country code)</FormLabel>
                <Input 
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+1234567890"
                />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>API ID</FormLabel>
                <Input 
                  value={apiId}
                  onChange={(e) => setApiId(e.target.value)}
                  placeholder="12345"
                />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>API Hash</FormLabel>
                <Input 
                  value={apiHash}
                  onChange={(e) => setApiHash(e.target.value)}
                  placeholder="0123456789abcdef0123456789abcdef"
                />
              </FormControl>
            </VStack>
          ) : (
            <VStack spacing={4}>
              <Text>
                A verification code has been sent to your Telegram app. Please enter it below.
              </Text>
              
              <FormControl isRequired>
                <FormLabel>Verification Code</FormLabel>
                <Input 
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="12345"
                />
              </FormControl>
            </VStack>
          )}
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          {step === 1 ? (
            <Button 
              colorScheme="blue" 
              onClick={handleSubmitCredentials}
              isDisabled={!phoneNumber || !apiId || !apiHash}
            >
              Send Code
            </Button>
          ) : (
            <Button 
              colorScheme="blue" 
              onClick={handleVerifyCode}
              isDisabled={!verificationCode}
            >
              Verify
            </Button>
          )}
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export const JoinGroupModal = ({ isOpen, onClose, onJoinGroup, accounts }) => {
  const [groupLink, setGroupLink] = useState('');
  const [selectedAccount, setSelectedAccount] = useState('');
  const toast = useToast();

  const handleJoinGroup = async () => {
    // This would connect to the backend API in a real implementation
    try {
      // Mock API call
      // const response = await fetch('/api/telegram/groups/join', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ 
      //     account_id: selectedAccount, 
      //     group_link: groupLink 
      //   })
      // });
      // const data = await response.json();
      
      // Mock response
      const mockGroup = {
        id: Math.floor(Math.random() * 1000),
        name: `Group from ${groupLink}`,
        username: groupLink.replace('@', '').replace('https://t.me/', ''),
        is_active: true
      };
      
      toast({
        title: 'Group joined successfully',
        description: 'Your account has joined the Telegram group',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      onJoinGroup(mockGroup);
      setGroupLink('');
      setSelectedAccount('');
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to join group',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Join Telegram Group</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <Text>
              Enter the Telegram group link or username and select which account should join the group.
            </Text>
            
            <FormControl isRequired>
              <FormLabel>Group Link or Username</FormLabel>
              <Input 
                value={groupLink}
                onChange={(e) => setGroupLink(e.target.value)}
                placeholder="@group_username or https://t.me/group_username"
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>Account</FormLabel>
              <Input 
                as="select"
                value={selectedAccount}
                onChange={(e) => setSelectedAccount(e.target.value)}
              >
                <option value="">Select an account</option>
                {accounts.map(account => (
                  <option key={account.id} value={account.id}>
                    {account.phone_number} {account.is_active ? '(Active)' : '(Inactive)'}
                  </option>
                ))}
              </Input>
            </FormControl>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button 
            colorScheme="blue" 
            onClick={handleJoinGroup}
            isDisabled={!groupLink || !selectedAccount}
          >
            Join Group
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export const GenerateSummaryModal = ({ isOpen, onClose, onGenerateSummary, groups }) => {
  const [selectedGroup, setSelectedGroup] = useState('');
  const [days, setDays] = useState(7);
  const toast = useToast();

  const handleGenerateSummary = async () => {
    // This would connect to the backend API in a real implementation
    try {
      // Mock API call
      // const response = await fetch('/api/summaries/generate', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ 
      //     group_id: selectedGroup, 
      //     days: days 
      //   })
      // });
      // const data = await response.json();
      
      toast({
        title: 'Summary generation started',
        description: 'Your summary is being generated and will be available soon',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
      
      // In a real implementation, this would be the actual summary from the API
      setTimeout(() => {
        const selectedGroupObj = groups.find(g => g.id.toString() === selectedGroup);
        const mockSummary = {
          id: Math.floor(Math.random() * 1000),
          group: selectedGroupObj,
          start_date: new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date().toISOString(),
          content: 'This is a mock summary of the group discussions for the selected period. In a real implementation, this would be generated by the AI model based on the collected messages.',
          created_at: new Date().toISOString()
        };
        
        onGenerateSummary(mockSummary);
        
        toast({
          title: 'Summary generated',
          description: 'Your summary is now available',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      }, 3000);
      
      setSelectedGroup('');
      setDays(7);
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to generate summary',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Generate Summary</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <Text>
              Select a group and time period to generate a summary of the messages.
            </Text>
            
            <FormControl isRequired>
              <FormLabel>Group</FormLabel>
              <Input 
                as="select"
                value={selectedGroup}
                onChange={(e) => setSelectedGroup(e.target.value)}
              >
                <option value="">Select a group</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </Input>
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>Time Period (days)</FormLabel>
              <Input 
                type="number"
                value={days}
                onChange={(e) => setDays(parseInt(e.target.value))}
                min={1}
                max={30}
              />
            </FormControl>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button 
            colorScheme="blue" 
            onClick={handleGenerateSummary}
            isDisabled={!selectedGroup || !days}
          >
            Generate
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
