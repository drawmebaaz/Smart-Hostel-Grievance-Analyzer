import React from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // Log to console for developers
    console.error('ErrorBoundary caught error:', error, errorInfo)
    
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }))
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  render() {
    if (this.state.hasError) {
      const isDegraded = this.state.errorCount > 3

      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-8 shadow-2xl">
              {/* Error Icon */}
              <div className="flex justify-center mb-4">
                <div className="bg-red-500/20 rounded-full p-3 border border-red-400/50">
                  <AlertCircle className="w-8 h-8 text-red-400" />
                </div>
              </div>

              {/* Error Title */}
              <h2 className="text-2xl font-bold text-white text-center mb-2">
                {isDegraded ? 'System Issue' : 'Something Went Wrong'}
              </h2>

              {/* Error Message - USER-FRIENDLY */}
              <p className="text-white/80 text-center mb-6">
                {isDegraded
                  ? 'The application encountered multiple errors. Please refresh the page.'
                  : 'An unexpected error occurred. Please try again or refresh the page.'}
              </p>

              {/* 🚨 REMOVE development error details from user view 🚨 */}
              {/* DELETE THIS ENTIRE SECTION for production: */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="mb-6 bg-red-500/10 border border-red-400/30 rounded-lg p-3 max-h-40 overflow-auto">
                  <p className="text-xs text-red-300 font-mono break-all">
                    {this.state.error.toString()}
                  </p>
                  {this.state.errorInfo?.componentStack && (
                    <p className="text-xs text-red-300/70 font-mono mt-2 whitespace-pre-wrap break-all">
                      {this.state.errorInfo.componentStack}
                    </p>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="space-y-2">
                {!isDegraded && (
                  <button
                    onClick={this.resetError}
                    className="w-full px-4 py-3 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-white font-medium flex items-center justify-center gap-2 mb-2 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Try Again
                  </button>
                )}
                <button
                  onClick={() => window.location.reload()}
                  className="w-full px-4 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium flex items-center justify-center gap-2 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh Page
                </button>
              </div>

              {/* Help Text */}
              <p className="text-xs text-white/50 text-center mt-4">
                Error ID: {new Date().toISOString()}
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary