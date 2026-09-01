import React, { useState } from 'react';
import { Upload, X, FileText, CheckCircle2 } from 'lucide-react';
import { DocumentType } from '../../api/types';
import { uploadDocument } from '../../api/client';

interface DocumentUploadProps {
  bidId: string;
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  bidId,
  isOpen,
  onClose,
  onUploadSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<DocumentType>('GST');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a document file (.pdf, .png, .jpg)');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      await uploadDocument(bidId, file, docType);
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setFile(null);
        onUploadSuccess();
        onClose();
      }, 1000);
    } catch (err: any) {
      setError(err.message || 'Failed to upload document.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-2xl z-10 flex flex-col gap-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Upload className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">Upload Bidder Document</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        {success ? (
          <div className="py-8 flex flex-col items-center justify-center text-center gap-2">
            <CheckCircle2 className="w-12 h-12 text-emerald-600" />
            <h4 className="font-bold text-slate-900 text-sm">Document Uploaded Successfully!</h4>
            <p className="text-xs text-slate-500">Document extracted and indexed in storage.</p>
          </div>
        ) : (
          <form onSubmit={handleUpload} className="flex flex-col gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Document Category
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value as DocumentType)}
                className="w-full text-xs font-semibold p-2.5 rounded-lg border border-slate-300 bg-slate-50 focus:bg-white focus:border-blue-500 outline-none"
              >
                <option value="GST">GST Registration Certificate</option>
                <option value="UDYAM">MSME Udyam Certificate</option>
                <option value="PAN">Income Tax PAN Card</option>
                <option value="EPFO">EPFO Statement / ECR</option>
                <option value="ESIC">ESIC Monthly Statement</option>
                <option value="OEM">OEM Authorization Letter (MAF)</option>
                <option value="DIGILOCKER">DigiLocker Certified Copy</option>
                <option value="BLACKLIST">Debarment Declaration</option>
                <option value="UNKNOWN">Other Supporting Document</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Select File (.PDF, .PNG, .JPG)
              </label>
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileChange}
                className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border border-slate-300 rounded-lg p-1.5"
              />
            </div>

            {error && (
              <div className="bg-rose-50 text-rose-700 text-xs font-medium p-2.5 rounded-lg border border-rose-200">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isUploading}
              className={`w-full py-2.5 rounded-lg text-xs font-bold text-white transition-all ${
                isUploading
                  ? 'bg-blue-300 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 active:scale-[0.99]'
              }`}
            >
              {isUploading ? 'Uploading & Processing OCR...' : 'Upload and Process Document'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
