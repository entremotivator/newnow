"""
Advanced Analytics Engine for Matrix VAPI Client
Comprehensive analytics, reporting, and performance monitoring
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import json
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class MatrixAnalyticsEngine:
    def __init__(self, database_manager):
        self.db = database_manager
        self.color_scheme = {
            'primary': '#00ff41',
            'secondary': '#ff0040', 
            'accent': '#4080ff',
            'warning': '#ffff00',
            'background': '#0a0a0a',
            'surface': '#1a1a2e'
        }
    
    def generate_comprehensive_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        # Get data
        call_records = self.db.get_call_records(limit=1000)
        agents = self.db.get_all_agents()
        metrics = self.db.get_metrics(start_date, end_date)
        
        # Convert to DataFrames
        calls_df = pd.DataFrame([{
            'id': call.id,
            'agent_id': call.agent_id,
            'agent_name': call.agent_name,
            'duration': call.duration,
            'cost': call.cost,
            'status': call.status,
            'started_at': call.started_at,
            'ended_at': call.ended_at,
            'sentiment_score': call.sentiment_score,
            'quality_score': call.quality_score
        } for call in call_records])
        
        agents_df = pd.DataFrame([{
            'id': agent.id,
            'name': agent.name,
            'category': agent.category,
            'matrix_level': agent.matrix_level,
            'cost_per_minute': agent.cost_per_minute,
            'usage_count': agent.usage_count,
            'avg_call_duration': agent.avg_call_duration,
            'success_rate': agent.success_rate
        } for agent in agents])
        
        # Generate report sections
        report = {
            'overview': self._generate_overview_metrics(calls_df, agents_df),
            'agent_performance': self._analyze_agent_performance(calls_df, agents_df),
            'cost_analysis': self._analyze_costs(calls_df, agents_df),
            'quality_metrics': self._analyze_quality_metrics(calls_df),
            'usage_patterns': self._analyze_usage_patterns(calls_df),
            'predictive_insights': self._generate_predictive_insights(calls_df),
            'recommendations': self._generate_recommendations(calls_df, agents_df)
        }
        
        return report
    
    def _generate_overview_metrics(self, calls_df: pd.DataFrame, agents_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate overview metrics"""
        if calls_df.empty:
            return {
                'total_calls': 0,
                'total_duration': 0,
                'total_cost': 0,
                'avg_call_duration': 0,
                'success_rate': 0,
                'active_agents': len(agents_df)
            }
        
        return {
            'total_calls': len(calls_df),
            'total_duration': calls_df['duration'].sum(),
            'total_cost': calls_df['cost'].sum(),
            'avg_call_duration': calls_df['duration'].mean(),
            'success_rate': (calls_df['status'] == 'completed').mean() * 100,
            'active_agents': len(agents_df[agents_df['status'] == 'active']),
            'avg_quality_score': calls_df['quality_score'].mean() if 'quality_score' in calls_df.columns else 0,
            'avg_sentiment_score': calls_df['sentiment_score'].mean() if 'sentiment_score' in calls_df.columns else 0
        }
    
    def _analyze_agent_performance(self, calls_df: pd.DataFrame, agents_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze individual agent performance"""
        if calls_df.empty:
            return {'agent_stats': [], 'top_performers': [], 'improvement_needed': []}
        
        # Group by agent
        agent_stats = calls_df.groupby('agent_name').agg({
            'duration': ['count', 'mean', 'sum'],
            'cost': 'sum',
            'quality_score': 'mean',
            'sentiment_score': 'mean'
        }).round(2)
        
        agent_stats.columns = ['call_count', 'avg_duration', 'total_duration', 'total_cost', 'avg_quality', 'avg_sentiment']
        agent_stats = agent_stats.reset_index()
        
        # Calculate performance scores
        agent_stats['performance_score'] = (
            agent_stats['avg_quality'] * 0.4 +
            agent_stats['avg_sentiment'] * 0.3 +
            (agent_stats['call_count'] / agent_stats['call_count'].max()) * 100 * 0.3
        )
        
        # Identify top performers and those needing improvement
        top_performers = agent_stats.nlargest(3, 'performance_score')[['agent_name', 'performance_score']].to_dict('records')
        improvement_needed = agent_stats.nsmallest(3, 'performance_score')[['agent_name', 'performance_score']].to_dict('records')
        
        return {
            'agent_stats': agent_stats.to_dict('records'),
            'top_performers': top_performers,
            'improvement_needed': improvement_needed
        }
    
    def _analyze_costs(self, calls_df: pd.DataFrame, agents_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cost patterns and efficiency"""
        if calls_df.empty:
            return {'total_cost': 0, 'cost_per_call': 0, 'cost_trends': []}
        
        # Cost analysis
        total_cost = calls_df['cost'].sum()
        cost_per_call = calls_df['cost'].mean()
        
        # Cost by agent
        cost_by_agent = calls_df.groupby('agent_name')['cost'].sum().sort_values(ascending=False)
        
        # Cost efficiency (cost per minute of quality interaction)
        calls_df['cost_efficiency'] = calls_df['cost'] / (calls_df['duration'] * calls_df['quality_score'])
        cost_efficiency = calls_df.groupby('agent_name')['cost_efficiency'].mean().sort_values()
        
        return {
            'total_cost': total_cost,
            'cost_per_call': cost_per_call,
            'cost_by_agent': cost_by_agent.to_dict(),
            'most_efficient_agents': cost_efficiency.head(5).to_dict(),
            'least_efficient_agents': cost_efficiency.tail(5).to_dict()
        }
    
    def _analyze_quality_metrics(self, calls_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze call quality and satisfaction metrics"""
        if calls_df.empty or 'quality_score' not in calls_df.columns:
            return {'avg_quality': 0, 'quality_distribution': {}}
        
        # Quality distribution
        quality_bins = pd.cut(calls_df['quality_score'], bins=[0, 2, 4, 6, 8, 10], labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'])
        quality_distribution = quality_bins.value_counts().to_dict()
        
        # Quality trends over time
        calls_df['date'] = pd.to_datetime(calls_df['started_at']).dt.date
        quality_trends = calls_df.groupby('date')['quality_score'].mean().to_dict()
        
        return {
            'avg_quality': calls_df['quality_score'].mean(),
            'quality_distribution': quality_distribution,
            'quality_trends': quality_trends,
            'quality_by_agent': calls_df.groupby('agent_name')['quality_score'].mean().to_dict()
        }
    
    def _analyze_usage_patterns(self, calls_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze usage patterns and trends"""
        if calls_df.empty:
            return {'peak_hours': [], 'peak_days': [], 'seasonal_trends': {}}
        
        calls_df['hour'] = pd.to_datetime(calls_df['started_at']).dt.hour
        calls_df['day_of_week'] = pd.to_datetime(calls_df['started_at']).dt.day_name()
        calls_df['date'] = pd.to_datetime(calls_df['started_at']).dt.date
        
        # Peak usage analysis
        peak_hours = calls_df['hour'].value_counts().head(5).to_dict()
        peak_days = calls_df['day_of_week'].value_counts().to_dict()
        
        # Daily trends
        daily_usage = calls_df.groupby('date').size().to_dict()
        
        return {
            'peak_hours': peak_hours,
            'peak_days': peak_days,
            'daily_usage': daily_usage,
            'avg_calls_per_day': calls_df.groupby('date').size().mean()
        }
    
    def _generate_predictive_insights(self, calls_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictive insights using machine learning"""
        if calls_df.empty or len(calls_df) < 10:
            return {'predictions': 'Insufficient data for predictions'}
        
        try:
            # Prepare data for clustering
            features = ['duration', 'cost', 'quality_score', 'sentiment_score']
            available_features = [f for f in features if f in calls_df.columns and calls_df[f].notna().any()]
            
            if len(available_features) < 2:
                return {'predictions': 'Insufficient feature data for analysis'}
            
            # Perform clustering to identify call patterns
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(calls_df[available_features].fillna(0))
            
            # Determine optimal number of clusters
            n_clusters = min(4, len(calls_df) // 3)
            if n_clusters < 2:
                n_clusters = 2
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(scaled_data)
            
            # Analyze clusters
            calls_df['cluster'] = clusters
            cluster_analysis = {}
            
            for cluster_id in range(n_clusters):
                cluster_data = calls_df[calls_df['cluster'] == cluster_id]
                cluster_analysis[f'Cluster_{cluster_id}'] = {
                    'size': len(cluster_data),
                    'avg_duration': cluster_data['duration'].mean(),
                    'avg_cost': cluster_data['cost'].mean(),
                    'characteristics': self._describe_cluster(cluster_data, available_features)
                }
            
            return {
                'call_patterns': cluster_analysis,
                'insights': self._generate_cluster_insights(cluster_analysis)
            }
        
        except Exception as e:
            return {'predictions': f'Analysis error: {str(e)}'}
    
    def _describe_cluster(self, cluster_data: pd.DataFrame, features: List[str]) -> str:
        """Describe characteristics of a cluster"""
        descriptions = []
        
        for feature in features:
            if feature in cluster_data.columns:
                avg_value = cluster_data[feature].mean()
                if feature == 'duration':
                    if avg_value > 300:  # 5 minutes
                        descriptions.append("Long duration calls")
                    elif avg_value < 60:  # 1 minute
                        descriptions.append("Short duration calls")
                elif feature == 'quality_score':
                    if avg_value > 8:
                        descriptions.append("High quality interactions")
                    elif avg_value < 5:
                        descriptions.append("Lower quality interactions")
                elif feature == 'cost':
                    if avg_value > 1.0:
                        descriptions.append("Higher cost calls")
                    elif avg_value < 0.5:
                        descriptions.append("Lower cost calls")
        
        return ", ".join(descriptions) if descriptions else "Standard calls"
    
    def _generate_cluster_insights(self, cluster_analysis: Dict) -> List[str]:
        """Generate insights from cluster analysis"""
        insights = []
        
        # Find largest cluster
        largest_cluster = max(cluster_analysis.items(), key=lambda x: x[1]['size'])
        insights.append(f"Most common call pattern: {largest_cluster[1]['characteristics']} ({largest_cluster[1]['size']} calls)")
        
        # Find highest cost cluster
        highest_cost_cluster = max(cluster_analysis.items(), key=lambda x: x[1]['avg_cost'])
        insights.append(f"Highest cost pattern: {highest_cost_cluster[1]['characteristics']} (${highest_cost_cluster[1]['avg_cost']:.2f} avg)")
        
        return insights
    
    def _generate_recommendations(self, calls_df: pd.DataFrame, agents_df: pd.DataFrame) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if calls_df.empty:
            recommendations.append("Start making calls to generate analytics data")
            return recommendations
        
        # Cost optimization recommendations
        if 'cost' in calls_df.columns:
            high_cost_agents = calls_df.groupby('agent_name')['cost'].mean().sort_values(ascending=False).head(3)
            if not high_cost_agents.empty:
                recommendations.append(f"Consider optimizing usage of high-cost agents: {', '.join(high_cost_agents.index)}")
        
        # Quality improvement recommendations
        if 'quality_score' in calls_df.columns:
            low_quality_agents = calls_df.groupby('agent_name')['quality_score'].mean().sort_values().head(3)
            if not low_quality_agents.empty and low_quality_agents.iloc[0] < 7:
                recommendations.append(f"Focus on improving quality for: {', '.join(low_quality_agents.index)}")
        
        # Usage pattern recommendations
        if 'started_at' in calls_df.columns:
            calls_df['hour'] = pd.to_datetime(calls_df['started_at']).dt.hour
            peak_hour = calls_df['hour'].mode().iloc[0] if not calls_df['hour'].mode().empty else 12
            recommendations.append(f"Peak usage is around {peak_hour}:00 - consider scaling resources accordingly")
        
        # Agent utilization recommendations
        if len(agents_df) > 0:
            total_calls = len(calls_df)
            calls_per_agent = calls_df['agent_name'].value_counts()
            underutilized = calls_per_agent[calls_per_agent < total_calls * 0.1].index.tolist()
            if underutilized:
                recommendations.append(f"Consider promoting underutilized agents: {', '.join(underutilized[:3])}")
        
        return recommendations
    
    def create_performance_dashboard(self, calls_df: pd.DataFrame, agents_df: pd.DataFrame) -> Dict[str, go.Figure]:
        """Create comprehensive performance dashboard"""
        figures = {}
        
        if calls_df.empty:
            # Create empty placeholder figures
            fig = go.Figure()
            fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(title="No Data Available", template="plotly_dark")
            return {"placeholder": fig}
        
        # 1. Call Volume Over Time
        if 'started_at' in calls_df.columns:
            calls_df['date'] = pd.to_datetime(calls_df['started_at']).dt.date
            daily_calls = calls_df.groupby('date').size().reset_index(name='call_count')
            
            fig_volume = px.line(daily_calls, x='date', y='call_count', 
                               title='📈 Call Volume Over Time',
                               color_discrete_sequence=[self.color_scheme['primary']])
            fig_volume.update_layout(template="plotly_dark", 
                                   paper_bgcolor=self.color_scheme['background'],
                                   plot_bgcolor=self.color_scheme['surface'])
            figures['call_volume'] = fig_volume
        
        # 2. Agent Performance Comparison
        if 'agent_name' in calls_df.columns:
            agent_metrics = calls_df.groupby('agent_name').agg({
                'duration': ['count', 'mean'],
                'cost': 'sum',
                'quality_score': 'mean'
            }).round(2)
            
            agent_metrics.columns = ['call_count', 'avg_duration', 'total_cost', 'avg_quality']
            agent_metrics = agent_metrics.reset_index()
            
            fig_performance = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Call Count', 'Average Duration', 'Total Cost', 'Average Quality'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Call count
            fig_performance.add_trace(
                go.Bar(x=agent_metrics['agent_name'], y=agent_metrics['call_count'],
                      name='Call Count', marker_color=self.color_scheme['primary']),
                row=1, col=1
            )
            
            # Average duration
            fig_performance.add_trace(
                go.Bar(x=agent_metrics['agent_name'], y=agent_metrics['avg_duration'],
                      name='Avg Duration', marker_color=self.color_scheme['accent']),
                row=1, col=2
            )
            
            # Total cost
            fig_performance.add_trace(
                go.Bar(x=agent_metrics['agent_name'], y=agent_metrics['total_cost'],
                      name='Total Cost', marker_color=self.color_scheme['secondary']),
                row=2, col=1
            )
            
            # Average quality
            if 'quality_score' in calls_df.columns:
                fig_performance.add_trace(
                    go.Bar(x=agent_metrics['agent_name'], y=agent_metrics['avg_quality'],
                          name='Avg Quality', marker_color=self.color_scheme['warning']),
                    row=2, col=2
                )
            
            fig_performance.update_layout(
                title='🎯 Agent Performance Comparison',
                template="plotly_dark",
                paper_bgcolor=self.color_scheme['background'],
                plot_bgcolor=self.color_scheme['surface'],
                showlegend=False
            )
            figures['agent_performance'] = fig_performance
        
        # 3. Cost Analysis
        if 'cost' in calls_df.columns and 'agent_name' in calls_df.columns:
            cost_by_agent = calls_df.groupby('agent_name')['cost'].sum().sort_values(ascending=False)
            
            fig_cost = px.pie(values=cost_by_agent.values, names=cost_by_agent.index,
                            title='💰 Cost Distribution by Agent',
                            color_discrete_sequence=px.colors.qualitative.Set3)
            fig_cost.update_layout(template="plotly_dark",
                                 paper_bgcolor=self.color_scheme['background'])
            figures['cost_distribution'] = fig_cost
        
        # 4. Quality Trends
        if 'quality_score' in calls_df.columns and 'started_at' in calls_df.columns:
            calls_df['date'] = pd.to_datetime(calls_df['started_at']).dt.date
            quality_trends = calls_df.groupby('date')['quality_score'].mean().reset_index()
            
            fig_quality = px.line(quality_trends, x='date', y='quality_score',
                                title='⭐ Quality Score Trends',
                                color_discrete_sequence=[self.color_scheme['accent']])
            fig_quality.update_layout(template="plotly_dark",
                                    paper_bgcolor=self.color_scheme['background'],
                                    plot_bgcolor=self.color_scheme['surface'])
            figures['quality_trends'] = fig_quality
        
        # 5. Usage Patterns Heatmap
        if 'started_at' in calls_df.columns:
            calls_df['hour'] = pd.to_datetime(calls_df['started_at']).dt.hour
            calls_df['day_of_week'] = pd.to_datetime(calls_df['started_at']).dt.day_name()
            
            usage_heatmap = calls_df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
            
            fig_heatmap = px.imshow(usage_heatmap.values,
                                  x=usage_heatmap.columns,
                                  y=usage_heatmap.index,
                                  title='🕐 Usage Patterns Heatmap',
                                  color_continuous_scale='Viridis')
            fig_heatmap.update_layout(template="plotly_dark",
                                    paper_bgcolor=self.color_scheme['background'])
            figures['usage_heatmap'] = fig_heatmap
        
        return figures
