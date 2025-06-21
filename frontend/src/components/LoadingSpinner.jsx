import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex justify-center items-center py-8">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-indigo-200 border-solid rounded-full animate-spin"></div>
        <div className="absolute top-0 left-0 w-12 h-12 border-4 border-indigo-600 border-solid rounded-full border-t-transparent animate-spin"></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
