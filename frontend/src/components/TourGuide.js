import React, { useState, useEffect } from 'react';
import Joyride, { STATUS } from 'react-joyride';

const TourGuide = ({ run, onFinish }) => {
  const steps = [
    {
      target: 'body',
      content: '👋 Welcome to CloudFlow Intelligence Platform! This comprehensive tour will guide you through all features. Let\'s begin your journey to intelligent cloud storage!',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '[data-tour="system-status"]',
      content: '📊 System Status: Monitor real-time services. Green = Connected. Kafka streams events, Email sends notifications, WebSocket provides live updates.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="kafka-stream"]',
      content: '🔴 Kafka Event Stream: Watch live events! Apache Kafka displays real-time migration progress, email notifications, and system events as they happen.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="generate-sample"]',
      content: '🎲 Generate Sample Data: Click to create 10 test files instantly! Perfect for exploring features without uploading real data. Try it now!',
      placement: 'bottom',
    },
    {
      target: '[data-tour="simulate-access"]',
      content: '🎯 Simulate Access Patterns: Train the AI by simulating file usage history. This helps the ML model learn and provide better cost-saving recommendations.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="summary-cards"]',
      content: '📈 Summary Cards: Your platform overview! Track total files, monthly costs, average latency, and active migrations at a glance.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="ml-recommendations"]',
      content: '💡 ML Recommendations: AI-powered cost optimization! The system analyzes access patterns and suggests tier changes or cloud moves to reduce costs. Click "Apply" to execute!',
      placement: 'top',
    },
    {
      target: '[data-tour="performance-metrics"]',
      content: '⚡ Performance Metrics: Track migration speed and reliability! See average latency, throughput (MB/s), success rate, and percentile breakdowns (P50/P90/P95/P99).',
      placement: 'top',
    },
    {
      target: '[data-tour="files-table"]',
      content: '📁 Your Files: Manage all data objects here. Each file shows its tier (Hot=fast/expensive, Warm=balanced, Cold=slow/cheap), location, and monthly cost. Click ↑ to migrate!',
      placement: 'top',
    },
    {
      target: '[data-tour="migrations-table"]',
      content: '🚀 Recent Migrations: Track your data movements! Real-time progress bars show migration status. Completed migrations appear with 100% progress.',
      placement: 'top',
    },
    {
      target: 'body',
      content: '📤 Upload Files: Need to add your own files? Use the "Upload" tab in the navigation menu to upload files directly to the platform. Supports various file types!',
      placement: 'center',
    },
    {
      target: 'body',
      content: '🔐 Cloud Credentials: Want real cloud migrations? Use the "Credentials" tab to add AWS, Azure, or GCP credentials. This enables actual file transfers to your cloud accounts!',
      placement: 'center',
    },
    {
      target: 'body',
      content: '🧭 Navigation Tips: Use the tabs at the top to switch between Dashboard, Upload, and Credentials. The ❓ button (bottom-right) restarts this tour anytime!',
      placement: 'center',
    },
    {
      target: 'body',
      content: '✨ You\'re Ready! You now know how to: generate sample data, upload files, add cloud credentials, manage migrations, and optimize costs with AI. Start optimizing your cloud storage!',
      placement: 'center',
    },
  ];

  const handleJoyrideCallback = (data) => {
    const { status } = data;
    const finishedStatuses = [STATUS.FINISHED, STATUS.SKIPPED];
    if (finishedStatuses.includes(status)) {
      localStorage.setItem('cloudflow-tour-completed', 'true');
      if (onFinish) onFinish();
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showProgress
      showSkipButton
      callback={handleJoyrideCallback}
      styles={{
        options: {
          primaryColor: '#0070f3',
          zIndex: 10000,
        },
        tooltip: {
          borderRadius: 8,
          fontSize: 16,
        },
        buttonNext: {
          backgroundColor: '#0070f3',
          borderRadius: 4,
          padding: '8px 16px',
        },
        buttonBack: {
          color: '#666',
          marginRight: 10,
        },
      }}
      locale={{
        back: 'Previous',
        close: 'Close',
        last: 'Finish',
        next: 'Next',
        skip: 'Skip Tour',
      }}
    />
  );
};

export default TourGuide;
