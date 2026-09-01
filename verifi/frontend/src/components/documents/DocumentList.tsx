import React, { useState } from 'react';
import { FileText, Upload, ChevronDown, ChevronUp, Folder } from 'lucide-react';
import { DocumentItem } from '../../api/types';
import { DocumentUpload } from './DocumentUpload';

interface DocumentListProps {
  documents: DocumentItem[];
  bidId: string;
  isLoading: boolean;
  onRefresh: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  bidId,
  isLoading,
  onRefresh,
}) => {
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [expandedDocId, setExpandedDocId] = useState<string | null>(null);

  const toggleExpand = (docId: string) => {
    setExpandedDocId(expandedDocId === docId ? null : docId);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Folder className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-800">Submitted Documents & Extracted Facts</h2>
        </div>
        <button
          onClick={() => setIsUploadOpen(true)}
          className="text-xs font-bold text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100/80 px-3 py-1.5 rounded-lg border border-blue-200 transition-colors flex items-center gap-1.5"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload Document</span>
        </button>
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-8 text-slate-400 text-sm italic">
          No documents uploaded for this bid. Click "Upload Document" above.
        </div>
      ) : (
        <div className="flex flex-col gap-2.5">
          {documents.map((doc) => {
            const isExpanded = expandedDocId === doc.id;
            const factCount = Object.keys(doc.extracted_facts || {}).length;

            return (
              <div
                key={doc.id}
                className="border border-slate-200 rounded-xl p-3 bg-white hover:border-slate-300 transition-all flex flex-col gap-2"
              >
                <div
                  onClick={() => toggleExpand(doc.id)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-50 text-blue-600 p-2 rounded-lg">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">{doc.file_name}</h4>
                      <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400 mt-0.5">
                        <span className="font-semibold text-slate-600">{doc.document_type}</span>
                        <span>•</span>
                        <span>{(doc.file_size_bytes / 1024).toFixed(1)} KB</span>
                        <span>•</span>
                        <span className="text-emerald-600">{doc.status}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="bg-sky-50 text-sky-700 text-[11px] font-semibold px-2 py-0.5 rounded border border-sky-200">
                      {factCount} facts extracted
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-2 pt-3 border-t border-slate-100 bg-slate-50 p-3 rounded-lg flex flex-col gap-2">
                    <span className="text-[11px] font-bold text-slate-600 uppercase">
                      Parsed Structured Fields:
                    </span>
                    <pre className="text-[11px] font-mono text-slate-800 bg-white p-2.5 rounded border border-slate-200 overflow-x-auto">
                      {JSON.stringify(doc.extracted_facts || {}, null, 2)}
                    </pre>
                    {doc.ocr_text_preview && (
                      <div className="mt-1">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">
                          OCR Text Snippet:
                        </span>
                        <p className="text-[11px] text-slate-600 bg-white p-2 rounded border border-slate-200 mt-1 font-mono line-clamp-3">
                          {doc.ocr_text_preview}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Upload Modal */}
      <DocumentUpload
        bidId={bidId}
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={onRefresh}
      />
    </div>
  );
};
