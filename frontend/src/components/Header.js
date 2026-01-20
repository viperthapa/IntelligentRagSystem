import React from 'react';

const Header = () => {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <h1 className="text-2xl font-semibold text-gray-800">Chat With Document</h1>
      <p className="text-sm text-gray-500 mt-1">
        Upload a document and ask questions about it
      </p>
    </div>
  );
}

export default Header;