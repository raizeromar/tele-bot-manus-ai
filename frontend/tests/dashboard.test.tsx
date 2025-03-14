import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import Dashboard from '../pages/dashboard';
import { AddAccountModal, JoinGroupModal, GenerateSummaryModal } from '../components/Modals';

// Mock the API calls
jest.mock('../utils/api', () => ({
  accountAPI: {
    getAccounts: jest.fn().mockResolvedValue({ data: [] }),
  },
  groupAPI: {
    getGroups: jest.fn().mockResolvedValue({ data: [] }),
  },
  summaryAPI: {
    getSummaries: jest.fn().mockResolvedValue({ data: [] }),
  },
}));

describe('Dashboard Component', () => {
  test('renders dashboard with tabs', () => {
    render(
      <ChakraProvider>
        <Dashboard />
      </ChakraProvider>
    );
    
    // Check if main elements are rendered
    expect(screen.getByText('Telegram AI Agent')).toBeInTheDocument();
    expect(screen.getByText('Summaries')).toBeInTheDocument();
    expect(screen.getByText('Accounts')).toBeInTheDocument();
    expect(screen.getByText('Groups')).toBeInTheDocument();
  });
  
  test('switches between tabs', async () => {
    render(
      <ChakraProvider>
        <Dashboard />
      </ChakraProvider>
    );
    
    // Default tab should be Summaries
    expect(screen.getByText('Weekly Summaries')).toBeInTheDocument();
    
    // Click on Accounts tab
    fireEvent.click(screen.getByText('Accounts'));
    await waitFor(() => {
      expect(screen.getByText('Telegram Accounts')).toBeInTheDocument();
    });
    
    // Click on Groups tab
    fireEvent.click(screen.getByText('Groups'));
    await waitFor(() => {
      expect(screen.getByText('Telegram Groups')).toBeInTheDocument();
    });
  });
});

describe('Modal Components', () => {
  test('AddAccountModal renders correctly', () => {
    const mockOnClose = jest.fn();
    const mockOnAddAccount = jest.fn();
    
    render(
      <ChakraProvider>
        <AddAccountModal 
          isOpen={true} 
          onClose={mockOnClose} 
          onAddAccount={mockOnAddAccount} 
        />
      </ChakraProvider>
    );
    
    expect(screen.getByText('Add Telegram Account')).toBeInTheDocument();
    expect(screen.getByText('Phone Number (with country code)')).toBeInTheDocument();
    expect(screen.getByText('API ID')).toBeInTheDocument();
    expect(screen.getByText('API Hash')).toBeInTheDocument();
  });
  
  test('JoinGroupModal renders correctly', () => {
    const mockOnClose = jest.fn();
    const mockOnJoinGroup = jest.fn();
    const mockAccounts = [
      { id: 1, phone_number: '+1234567890', is_active: true }
    ];
    
    render(
      <ChakraProvider>
        <JoinGroupModal 
          isOpen={true} 
          onClose={mockOnClose} 
          onJoinGroup={mockOnJoinGroup}
          accounts={mockAccounts}
        />
      </ChakraProvider>
    );
    
    expect(screen.getByText('Join Telegram Group')).toBeInTheDocument();
    expect(screen.getByText('Group Link or Username')).toBeInTheDocument();
    expect(screen.getByText('Account')).toBeInTheDocument();
  });
  
  test('GenerateSummaryModal renders correctly', () => {
    const mockOnClose = jest.fn();
    const mockOnGenerateSummary = jest.fn();
    const mockGroups = [
      { id: 1, name: 'Test Group', is_active: true }
    ];
    
    render(
      <ChakraProvider>
        <GenerateSummaryModal 
          isOpen={true} 
          onClose={mockOnClose} 
          onGenerateSummary={mockOnGenerateSummary}
          groups={mockGroups}
        />
      </ChakraProvider>
    );
    
    expect(screen.getByText('Generate Summary')).toBeInTheDocument();
    expect(screen.getByText('Group')).toBeInTheDocument();
    expect(screen.getByText('Time Period (days)')).toBeInTheDocument();
  });
});
