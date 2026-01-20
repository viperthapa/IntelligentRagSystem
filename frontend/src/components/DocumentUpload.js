import React, { useRef } from 'react';
import { Upload, File, X, Loader2 } from 'lucide-react';

const DocumentUpload = (props) => {

    const { uploadedFile, isUploading, uploadError, onFileSelect, onRemoveFile } = props;
    const fileInputRef = useRef(null);

    return (
        <div className="bg-white border-b border-gray-200 px-6 py-4">
        {!uploadedFile ? (
            <div className="flex items-center gap-4">
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md"
                onChange={onFileSelect}
                className="hidden"
                id="file-upload"
            />
            <label
                htmlFor="file-upload"
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
            >
                {isUploading ? (
                <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Uploading...</span>
                </>
                ) : (
                <>
                    <Upload className="w-5 h-5" />
                    <span>Upload Document</span>
                </>
                )}
            </label>
            <span className="text-sm text-gray-500">
                Supports PDF, TXT, and Markdown files
            </span>
            </div>
        ) : (
            <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
            <div className="flex items-center gap-3">
                <File className="w-5 h-5 text-blue-600" />
                <div>
                <p className="font-medium text-gray-800">{uploadedFile.name}</p>
                </div>
            </div>
            <button
                onClick={onRemoveFile}
                className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
                title="Remove file"
            >
                <X className="w-5 h-5 text-gray-600" />
            </button>
            </div>
        )}
        {uploadError && (
            <p className="text-sm text-red-600 mt-2">{uploadError}</p>
        )}
        </div>
    );
}

export default DocumentUpload;