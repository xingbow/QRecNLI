/**
 * Configuration Storage Service
 * Handles persistence of chart configurations and titles
 */

class ConfigStorageService {
  constructor() {
    this.storageKey = 'chartConfigurations';
    this.titleStorageKey = 'chartTitles';
  }

  /**
   * Save chart configuration for a specific chart
   * @param {string} chartId - Unique identifier for the chart
   * @param {Object} config - Chart configuration object
   */
  saveChartConfig(chartId, config) {
    try {
      const configs = this.getAllChartConfigs();
      configs[chartId] = {
        ...config,
        timestamp: Date.now(),
        chartId: chartId
      };
      localStorage.setItem(this.storageKey, JSON.stringify(configs));
      console.log(`Saved configuration for chart: ${chartId}`, config);
    } catch (error) {
      console.error('Error saving chart configuration:', error);
    }
  }

  /**
   * Retrieve chart configuration for a specific chart
   * @param {string} chartId - Unique identifier for the chart
   * @returns {Object|null} - Chart configuration or null if not found
   */
  getChartConfig(chartId) {
    try {
      const configs = this.getAllChartConfigs();
      return configs[chartId] || null;
    } catch (error) {
      console.error('Error retrieving chart configuration:', error);
      return null;
    }
  }

  /**
   * Get all chart configurations
   * @returns {Object} - All stored chart configurations
   */
  getAllChartConfigs() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error retrieving all chart configurations:', error);
      return {};
    }
  }

  /**
   * Save chart title for a specific chart
   * @param {string} chartId - Unique identifier for the chart
   * @param {string} title - Chart title
   */
  saveChartTitle(chartId, title) {
    try {
      const titles = this.getAllChartTitles();
      titles[chartId] = {
        title: title,
        timestamp: Date.now(),
        chartId: chartId
      };
      localStorage.setItem(this.titleStorageKey, JSON.stringify(titles));
      console.log(`Saved title for chart: ${chartId}`, title);
    } catch (error) {
      console.error('Error saving chart title:', error);
    }
  }

  /**
   * Retrieve chart title for a specific chart
   * @param {string} chartId - Unique identifier for the chart
   * @returns {string|null} - Chart title or null if not found
   */
  getChartTitle(chartId) {
    try {
      const titles = this.getAllChartTitles();
      return titles[chartId] ? titles[chartId].title : null;
    } catch (error) {
      console.error('Error retrieving chart title:', error);
      return null;
    }
  }

  /**
   * Get all chart titles
   * @returns {Object} - All stored chart titles
   */
  getAllChartTitles() {
    try {
      const stored = localStorage.getItem(this.titleStorageKey);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error retrieving all chart titles:', error);
      return {};
    }
  }

  /**
   * Save complete chart state (configuration + title)
   * @param {string} chartId - Unique identifier for the chart
   * @param {Object} config - Chart configuration
   * @param {string} title - Chart title
   */
  saveChartState(chartId, config, title) {
    this.saveChartConfig(chartId, config);
    this.saveChartTitle(chartId, title);
  }

  /**
   * Retrieve complete chart state (configuration + title)
   * @param {string} chartId - Unique identifier for the chart
   * @returns {Object} - Object containing config and title
   */
  getChartState(chartId) {
    return {
      config: this.getChartConfig(chartId),
      title: this.getChartTitle(chartId)
    };
  }

  /**
   * Delete configuration and title for a specific chart
   * @param {string} chartId - Unique identifier for the chart
   */
  deleteChartState(chartId) {
    try {
      const configs = this.getAllChartConfigs();
      const titles = this.getAllChartTitles();
      
      delete configs[chartId];
      delete titles[chartId];
      
      localStorage.setItem(this.storageKey, JSON.stringify(configs));
      localStorage.setItem(this.titleStorageKey, JSON.stringify(titles));
      
      console.log(`Deleted state for chart: ${chartId}`);
    } catch (error) {
      console.error('Error deleting chart state:', error);
    }
  }

  /**
   * Clear all stored configurations and titles
   */
  clearAllStates() {
    try {
      localStorage.removeItem(this.storageKey);
      localStorage.removeItem(this.titleStorageKey);
      console.log('Cleared all chart states');
    } catch (error) {
      console.error('Error clearing all chart states:', error);
    }
  }

  /**
   * Get storage statistics
   * @returns {Object} - Storage usage information
   */
  getStorageStats() {
    try {
      const configs = this.getAllChartConfigs();
      const titles = this.getAllChartTitles();
      
      return {
        totalCharts: Object.keys(configs).length,
        totalConfigs: Object.keys(configs).length,
        totalTitles: Object.keys(titles).length,
        lastUpdated: Math.max(...Object.values(configs).map(c => c.timestamp || 0), 0)
      };
    } catch (error) {
      console.error('Error getting storage stats:', error);
      return { totalCharts: 0, totalConfigs: 0, totalTitles: 0, lastUpdated: 0 };
    }
  }
}

// Export singleton instance
export default new ConfigStorageService();
