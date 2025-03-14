# Telegram AI Agent - User Documentation

## Introduction

Welcome to the Telegram AI Agent! This application allows you to monitor Telegram groups, collect messages, and generate AI-powered summaries. This documentation will guide you through setting up and using the system.

## Getting Started

### Account Registration

1. Navigate to the login page
2. Click on "Sign Up" to create a new account
3. Fill in your username, email, and password
4. Click "Sign Up" to complete registration
5. You will be automatically logged in after successful registration

### Logging In

1. Navigate to the login page
2. Enter your username and password
3. Click "Sign In" to access your dashboard

## Dashboard Overview

The dashboard is divided into three main sections:

1. **Summaries** - View and manage AI-generated summaries of your Telegram groups
2. **Accounts** - Manage your Telegram accounts
3. **Groups** - View and manage the Telegram groups you're monitoring

## Managing Telegram Accounts

### Adding a Telegram Account

1. Navigate to the "Accounts" tab
2. Click "Add New Account"
3. Enter your phone number with country code (e.g., +1234567890)
4. Enter your API ID and API Hash (obtained from https://my.telegram.org/apps)
5. Click "Send Code" to receive a verification code on Telegram
6. Enter the verification code you received
7. Click "Verify" to complete the process

### Managing Existing Accounts

- **Activate/Deactivate**: Toggle the status of an account to control whether it collects messages
- **Remove**: Delete an account from the system

## Managing Telegram Groups

### Joining a Group

1. Navigate to the "Groups" tab
2. Click "Join New Group"
3. Enter the group link or username (e.g., @group_name or https://t.me/group_name)
4. Select which of your Telegram accounts should join the group
5. Click "Join Group" to complete the process

### Managing Group Monitoring

- **View Messages**: See the most recent messages collected from a group
- **Generate Summary**: Manually trigger a summary generation for a specific group
- **Activate/Deactivate**: Control whether a group is actively being monitored

## Working with Summaries

### Viewing Summaries

1. Navigate to the "Summaries" tab
2. Browse through the list of available summaries
3. Click "View Full Summary" to see the complete content

### Generating New Summaries

1. Click "Generate New Summary" on the Summaries tab
   - OR -
   Navigate to a specific group and click "Generate Summary"
2. Select the group you want to summarize
3. Choose the time period (in days) for the summary
4. Click "Generate" to start the process

### Providing Feedback

1. View a summary
2. Scroll to the bottom to find the feedback section
3. Rate the summary (1-5 stars)
4. Optionally add a comment
5. Click "Submit Feedback" to help improve future summaries

## Automatic Features

The system includes several automatic features:

- **Weekly Message Collection**: Messages are automatically collected from all active groups
- **Weekly Summaries**: Summaries are automatically generated once a week
- **Inactive Association Detection**: The system will mark associations as inactive if no messages are collected for a week

## Troubleshooting

### Account Connection Issues

- Ensure your API ID and API Hash are correct
- Check that your phone number is in the correct format with country code
- Verify that you have an active internet connection
- Make sure your Telegram account is not restricted or banned

### Group Joining Problems

- Verify that the group link or username is correct
- Ensure the selected Telegram account has permission to join the group
- Check if the group is private and requires an invitation

### Summary Generation Issues

- Ensure there are messages collected for the selected time period
- Check that your Google API key is valid and has access to Gemini 2.0 Flash
- Verify that the group and account association is active

## Getting Help

If you encounter any issues not covered in this documentation, please contact support at support@example.com.
