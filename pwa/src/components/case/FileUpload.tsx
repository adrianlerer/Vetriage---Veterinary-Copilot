import { useState, useRef, useCallback } from 'react'
import { Upload, X, FileImage, FileText, Film, Eye } from 'lucide-react'

export interface UploadedFile {
  id: string
  file: File
  preview?: string
  type: 'image' | 'document' | 'video' | 'other'
  category: string
}

const FILE_CATEGORIES = [
  'Radiografía',
  'Ecografía',
  'Análisis de sangre',
  'Análisis de orina',
  'Histopatología',
  'Electrocardiograma',
  'Fotografía clínica',
  'Otro',
]

interface Props {
  files: UploadedFile[]
  onChange: (files: UploadedFile[]) => void
}

function getFileType(file: File): UploadedFile['type'] {
  if (file.type.startsWith('image/')) return 'image'
  if (file.type.startsWith('video/')) return 'video'
  if (file.type.includes('pdf') || file.type.includes('document') || file.type.includes('text'))
    return 'document'
  return 'other'
}

export function FileUpload({ files, onChange }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [previewFile, setPreviewFile] = useState<UploadedFile | null>(null)

  const addFiles = useCallback(
    (newFiles: FileList | File[]) => {
      const additions: UploadedFile[] = Array.from(newFiles).map((file) => {
        const type = getFileType(file)
        const preview = type === 'image' ? URL.createObjectURL(file) : undefined
        return {
          id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
          file,
          preview,
          type,
          category: type === 'image' ? 'Fotografía clínica' : 'Otro',
        }
      })
      onChange([...files, ...additions])
    },
    [files, onChange]
  )

  const removeFile = (id: string) => {
    const f = files.find((f) => f.id === id)
    if (f?.preview) URL.revokeObjectURL(f.preview)
    onChange(files.filter((f) => f.id !== id))
  }

  const updateCategory = (id: string, category: string) => {
    onChange(files.map((f) => (f.id === id ? { ...f, category } : f)))
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files)
  }

  const FileIcon = ({ type }: { type: UploadedFile['type'] }) => {
    switch (type) {
      case 'image': return <FileImage className="w-5 h-5 text-blue-500" />
      case 'video': return <Film className="w-5 h-5 text-purple-500" />
      case 'document': return <FileText className="w-5 h-5 text-orange-500" />
      default: return <FileText className="w-5 h-5 text-slate-400" />
    }
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-200 cursor-pointer ${
          dragOver
            ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20'
            : 'border-slate-300 dark:border-slate-600 hover:border-brand-400 hover:bg-slate-50 dark:hover:bg-slate-800/50'
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept="image/*,video/*,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.dicom,.dcm"
          className="hidden"
          onChange={(e) => e.target.files && addFiles(e.target.files)}
        />
        <Upload className={`w-10 h-10 mx-auto mb-3 ${dragOver ? 'text-brand-500' : 'text-slate-400'}`} />
        <p className="font-medium text-slate-700 dark:text-slate-200">
          Arrastrá archivos o hacé clic para subir
        </p>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Imágenes, radiografías, ecografías, análisis, PDFs, videos
        </p>
        <p className="text-xs text-slate-400 mt-2">
          Formatos: JPG, PNG, PDF, DICOM, MP4, DOC, XLS y más
        </p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
            {files.length} archivo{files.length !== 1 ? 's' : ''} adjunto{files.length !== 1 ? 's' : ''}
          </p>
          {files.map((f) => (
            <div
              key={f.id}
              className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-700/50 group"
            >
              {/* Thumbnail or icon */}
              {f.preview ? (
                <button
                  type="button"
                  onClick={() => setPreviewFile(f)}
                  className="relative w-12 h-12 rounded-lg overflow-hidden flex-shrink-0 hover:ring-2 hover:ring-brand-500 transition-all"
                >
                  <img src={f.preview} alt="" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/0 hover:bg-black/20 flex items-center justify-center transition-colors">
                    <Eye className="w-4 h-4 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </button>
              ) : (
                <div className="w-12 h-12 rounded-lg bg-slate-200 dark:bg-slate-600 flex items-center justify-center flex-shrink-0">
                  <FileIcon type={f.type} />
                </div>
              )}

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{f.file.name}</p>
                <p className="text-xs text-slate-400">
                  {(f.file.size / 1024).toFixed(0)} KB
                </p>
              </div>

              {/* Category selector */}
              <select
                className="text-xs bg-white dark:bg-slate-600 border border-slate-200 dark:border-slate-500 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand-500"
                value={f.category}
                onChange={(e) => updateCategory(f.id, e.target.value)}
                onClick={(e) => e.stopPropagation()}
              >
                {FILE_CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>

              {/* Remove */}
              <button
                type="button"
                onClick={() => removeFile(f.id)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Preview modal */}
      {previewFile && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
          onClick={() => setPreviewFile(null)}
        >
          <div className="relative max-w-4xl max-h-[90vh] w-full" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setPreviewFile(null)}
              className="absolute -top-3 -right-3 z-10 p-2 bg-white dark:bg-slate-700 rounded-full shadow-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <img
              src={previewFile.preview}
              alt={previewFile.file.name}
              className="w-full h-auto max-h-[85vh] object-contain rounded-2xl shadow-2xl"
            />
            <p className="text-center text-white text-sm mt-3">
              {previewFile.file.name} · {previewFile.category}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
