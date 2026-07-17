# Dashboard Components for SEO Gap Analysis

Reusable React components and patterns for creating SEO gap analysis dashboards.

## GTV Brand Colors

```javascript
const colors = {
  // Primary gradient
  primary: '#00CCFF',     // Cyan
  secondary: '#4DA6E8',   // Light blue
  tertiary: '#7A7FD1',    // Purple-blue
  quaternary: '#A758BA',  // Purple
  accent: '#850DBA',      // Deep purple
  
  // Status colors
  positive: '#00CC99',    // Green - for wins/positives
  negative: '#FF6B6B',    // Red - for gaps/negatives
  warning: '#FFB347',     // Orange - for warnings
  
  // Neutral
  text: '#2D2D2D',
  subtext: '#666666',
  background: '#F8F9FA',
  cardBg: '#FFFFFF',
  
  // Chart colors array
  chartColors: ['#00CCFF', '#4DA6E8', '#7A7FD1', '#A758BA', '#850DBA', '#00CC99', '#FFB347', '#FF6B6B']
};
```

## Priority Color Mapping

```javascript
const getPriorityColor = (priority) => {
  switch(priority) {
    case 'CRITICAL':
    case 'P0':
      return colors.negative;
    case 'HIGH':
    case 'P1':
      return colors.warning;
    case 'MEDIUM':
    case 'P2':
      return colors.primary;
    case 'LOW':
    case 'P3':
    case 'OK':
      return colors.positive;
    default:
      return colors.tertiary;
  }
};

const getGapColor = (gapPercent) => {
  if (gapPercent > 80) return colors.negative;
  if (gapPercent > 50) return colors.warning;
  if (gapPercent > 30) return colors.primary;
  return colors.positive;
};
```

## Component Patterns

### 1. Executive Summary Banner

```jsx
const ExecutiveSummaryBanner = ({ metrics }) => (
  <div className="bg-white rounded-xl p-6 shadow-md mb-8 border-l-4" 
       style={{ borderColor: colors.accent }}>
    <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
      <Award className="w-6 h-6" style={{ color: colors.accent }} />
      Executive Summary: {metrics.title}
    </h2>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {metrics.cards.map((card, index) => (
        <div key={index} className="p-4 rounded-lg" 
             style={{ backgroundColor: card.isPositive ? '#E6FAF5' : card.isNegative ? '#FFE6E6' : '#FFF8E6' }}>
          <div className="text-3xl font-bold mb-1" 
               style={{ color: card.isPositive ? colors.positive : card.isNegative ? colors.negative : colors.warning }}>
            {card.value}
          </div>
          <div className="text-sm font-semibold text-gray-700">{card.label}</div>
          <div className="text-xs text-gray-500">{card.subtitle}</div>
        </div>
      ))}
    </div>
  </div>
);
```

### 2. Gap Card Component

```jsx
const GapCard = ({ title, current, target, gap, priority, icon: Icon }) => (
  <div className="bg-white rounded-xl p-4 shadow-md border border-gray-100">
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-2">
        <Icon className="w-5 h-5" style={{ color: getPriorityColor(priority) }} />
        <span className="font-semibold text-gray-800">{title}</span>
      </div>
      <span className="px-2 py-1 rounded-full text-xs font-bold text-white" 
            style={{ backgroundColor: getPriorityColor(priority) }}>
        {priority}
      </span>
    </div>
    <div className="grid grid-cols-3 gap-2 text-sm">
      <div>
        <div className="text-gray-500 text-xs">Current</div>
        <div className="font-bold text-gray-700">{current}</div>
      </div>
      <div>
        <div className="text-gray-500 text-xs">Target</div>
        <div className="font-bold text-green-600">{target}</div>
      </div>
      <div>
        <div className="text-gray-500 text-xs">Gap</div>
        <div className="font-bold" style={{ color: colors.negative }}>{gap}</div>
      </div>
    </div>
  </div>
);
```

### 3. Strategy Roadmap Card

```jsx
const StrategyCard = ({ phase, title, items, color, timeline }) => (
  <div className="bg-white rounded-xl p-5 shadow-md border-t-4" style={{ borderColor: color }}>
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <span className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
              style={{ backgroundColor: color }}>
          {phase}
        </span>
        <h3 className="font-bold text-gray-800">{title}</h3>
      </div>
      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{timeline}</span>
    </div>
    <ul className="space-y-2">
      {items.map((item, idx) => (
        <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
          <ArrowRight className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color }} />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  </div>
);
```

### 4. Stat Card Component

```jsx
const StatCard = ({ icon: Icon, title, value, subtitle, color, isPositive, isNegative }) => (
  <div className="bg-white rounded-xl p-5 shadow-md border-l-4 hover:shadow-lg transition-shadow"
       style={{ borderColor: isPositive ? colors.positive : isNegative ? colors.negative : color }}>
    <div className="flex items-center gap-3 mb-3">
      <div className="p-2 rounded-lg" 
           style={{ backgroundColor: `${isPositive ? colors.positive : isNegative ? colors.negative : color}20` }}>
        <Icon className="w-5 h-5" 
              style={{ color: isPositive ? colors.positive : isNegative ? colors.negative : color }} />
      </div>
      <span className="text-gray-500 text-sm font-medium">{title}</span>
    </div>
    <div className="text-2xl font-bold" 
         style={{ color: isPositive ? colors.positive : isNegative ? colors.negative : colors.text }}>
      {value}
    </div>
    {subtitle && <div className="text-sm text-gray-500 mt-1">{subtitle}</div>}
  </div>
);
```

### 5. Comparison Table

```jsx
const ComparisonTable = ({ data, columns, highlightColumn }) => (
  <div className="bg-white rounded-xl p-6 shadow-md">
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b-2">
            {columns.map((col, idx) => (
              <th key={idx} className="text-left py-3 px-4 font-bold text-gray-700">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr key={rowIdx} className="border-b hover:bg-gray-50">
              {columns.map((col, colIdx) => (
                <td key={colIdx} className="py-3 px-4"
                    style={{ 
                      fontWeight: colIdx === highlightColumn ? 'bold' : 'normal',
                      color: col.colorFn ? col.colorFn(row[col.key]) : colors.text 
                    }}>
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);
```

## Chart Patterns

### 1. Gap Bar Chart (Horizontal)

```jsx
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={gapData} layout="vertical" margin={{ left: 10, right: 20 }}>
    <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
    <XAxis type="number" domain={[-100, 0]} tickFormatter={(v) => `${v}%`} />
    <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11 }} />
    <Tooltip content={<CustomTooltip />} />
    <Bar dataKey="gap" radius={[0, 4, 4, 0]}>
      {gapData.map((entry, index) => (
        <Cell key={index} fill={getGapColor(Math.abs(entry.gap))} />
      ))}
    </Bar>
  </BarChart>
</ResponsiveContainer>
```

### 2. Radar Chart (Structure Comparison)

```jsx
<ResponsiveContainer width="100%" height={300}>
  <RadarChart data={radarData}>
    <PolarGrid />
    <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
    <PolarRadiusAxis angle={30} domain={[0, 100]} />
    <Radar name="Your Site" dataKey="yours" stroke={colors.primary} fill={colors.primary} fillOpacity={0.3} />
    <Radar name="Competitor" dataKey="competitor" stroke={colors.positive} fill={colors.positive} fillOpacity={0.3} />
    <Legend />
  </RadarChart>
</ResponsiveContainer>
```

### 3. Distribution Pie Chart

```jsx
<ResponsiveContainer width="100%" height={250}>
  <PieChart>
    <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} 
         dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
      {pieData.map((entry, index) => (
        <Cell key={index} fill={colors.chartColors[index % colors.chartColors.length]} />
      ))}
    </Pie>
    <Tooltip />
    <Legend />
  </PieChart>
</ResponsiveContainer>
```

### 4. Traffic Projection Line

```jsx
<ResponsiveContainer width="100%" height={250}>
  <LineChart data={projectionData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="month" />
    <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} />
    <Tooltip />
    <Line type="monotone" dataKey="current" stroke={colors.primary} strokeWidth={2} name="Projected" />
    <Line type="monotone" dataKey="benchmark" stroke={colors.positive} strokeDasharray="5 5" name="Benchmark" />
    <Legend />
  </LineChart>
</ResponsiveContainer>
```

## Layout Templates

### Full Dashboard Layout

```jsx
export default function SEOGapDashboard() {
  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: colors.background }}>
      {/* Header */}
      <Header title="SEO Gap Analysis" subtitle="Client Name | Website Type" />
      
      {/* Executive Summary */}
      <ExecutiveSummaryBanner metrics={summaryMetrics} />
      
      {/* Critical Gaps Section */}
      <Section title="🔴 Critical Gaps" icon={AlertTriangle}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {criticalGaps.map((gap, idx) => <GapCard key={idx} {...gap} />)}
        </div>
      </Section>
      
      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ChartCard title="Structure Comparison">
          <RadarChart ... />
        </ChartCard>
        <ChartCard title="Traffic Gap by Segment">
          <BarChart ... />
        </ChartCard>
      </div>
      
      {/* Comparison Table */}
      <ComparisonTable data={comparisonData} columns={columns} />
      
      {/* Strategy Roadmap */}
      <Section title="🎯 Strategy Roadmap" icon={Zap}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {phases.map((phase, idx) => <StrategyCard key={idx} {...phase} />)}
        </div>
      </Section>
      
      {/* Key Takeaways */}
      <KeyTakeaways items={takeaways} />
      
      {/* Footer */}
      <Footer brand="GTV SEO Agency" />
    </div>
  );
}
```

## Data Structure Templates

### Gap Analysis Data

```javascript
const gapData = [
  { name: 'Category A', yours: 1000, benchmark: 5000, gap: -80, priority: 'CRITICAL' },
  { name: 'Category B', yours: 2000, benchmark: 3000, gap: -33, priority: 'MEDIUM' },
  // ...
];
```

### Strategy Phases Data

```javascript
const strategyPhases = [
  {
    phase: 'P0',
    title: 'Quick Wins',
    color: colors.negative,
    timeline: 'Week 1-4',
    items: ['Action 1', 'Action 2', 'Action 3']
  },
  // ...
];
```

### Comparison Data

```javascript
const comparisonData = [
  { site: 'Your Site', traffic: 100000, category: 45, company: 1000, gap: 0 },
  { site: 'Competitor 1', traffic: 500000, category: 55, company: 5000, gap: -80 },
  // ...
];
```

## Lucide Icons to Use

```javascript
import { 
  Target,           // Header/goals
  TrendingUp,       // Growth metrics
  AlertTriangle,    // Warnings/gaps
  CheckCircle,      // Completed/wins
  Lightbulb,        // Insights
  Zap,              // Quick actions
  MapPin,           // Location
  Building2,        // Company/business
  FileText,         // Documents/content
  Calculator,       // Tools
  Users,            // Audience/team
  Briefcase,        // Jobs/work
  Award,            // Achievements
  ArrowRight,       // List items
  Layers,           // Structure
  Globe,            // International
  Star              // Priority/featured
} from 'lucide-react';
```

## Required Imports

```javascript
import React from 'react';
import { 
  PieChart, Pie, Cell,
  BarChart, Bar, 
  LineChart, Line,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Legend 
} from 'recharts';
```
