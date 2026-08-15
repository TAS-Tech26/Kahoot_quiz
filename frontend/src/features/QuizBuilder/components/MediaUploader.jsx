// MediaUploader.jsx


import {useState} from 'react'

import {apiCall} from '../../../api/api'


export default function MediaUploader({onUploadSuccess, onRemove, setIsUploading, currentMediaUrl, currentMediaType}) {

    const [localLoading, setLocalLoading] = useState(false)

    const handleFileChange = async (e) => {
        const file = e.target.files[0]

        if (!file) return

        const MAX_SIZE = 50 * 1024 * 1024

        if (file.size > MAX_SIZE) {
            alert("File exceeds 50MB limit. Compress it & try again.")

            e.target.value = null

            return
        }

        let derivedType = 'image'
        
        const ext = file.name.split('.').pop().toLowerCase()

        if (['mp4', 'webm', 'ogg', 'mov', 'mkv'].includes(ext) || file.type.startsWith('video/')) {
            derivedType = 'video'
        } else if (['mp3', 'wav', 'm4a', 'aac'].includes(ext) || file.type.startsWith('audio/')) {
            derivedType = 'audio'
        }

        setLocalLoading(true)
        setIsUploading(true)

        try {
            const sigResponse = await apiCall('/media/signature/')

            if (!sigResponse.ok) throw new Error("Failed to authenticate upload with server.")

            const {signature, timestamp, api_key, cloud_name} = await sigResponse.json()

            const formData = new FormData()

            formData.append('file', file)
            formData.append('api_key', api_key)
            formData.append('timestamp', timestamp)
            formData.append('signature', signature)
            formData.append('folder', 'kahoot_media')

            const uploadResponse = await fetch(`https://api.cloudinary.com/v1_1/${cloud_name}/auto/upload`, {method : 'POST', body : formData})
            const uploadData = await uploadResponse.json()

            if (!uploadResponse.ok) throw new Error(uploadData.error?.message || "Cloudinary rejected the upload.")

            onUploadSuccess(uploadData.secure_url, derivedType)
        } catch (error) {
            console.error("Upload error : ", error)

            alert(`Upload failed: ${error.message}`)
        } finally {
            setLocalLoading(false)
            setIsUploading(false)

            e.target.value = null
        }
    }

    return (

        <div className = "border-4 border-ink bg-bg-base p-4 text-center relative shadow-brutal-sm">
            {localLoading && (
                <div className = "absolute inset-0 bg-white/80 flex items-center justify-center font-bold z-10">
                    Uploading to Cloudinary...
                </div>
            )}

            {!currentMediaUrl ? (
                <div>
                    <p className = "text-sm text-gray-500 mb-2">
                        Attach Image, Video or Audio (Max 50MB)
                    </p>

                    <input
                        type = 'file'
                        accept = 'image/*, video/*, audio/*'
                        onChange = {handleFileChange}
                        className = 'text-sm'
                        disabled = {localLoading}
                    />
                </div>
            ) : (
                <div className = "flex flex-col items-center">
                    <p className = "text-green-600 font-bold text-sm mb-2">
                        Media Attached ({currentMediaType})
                    </p>

                    {currentMediaType === 'image' && (
                        <img
                            src = {currentMediaUrl}
                            alt = "Question Media"
                            className = "h-32 object-contain rounded"
                        />
                    )}

                    {currentMediaType === 'video' && (
                        <video
                            src = {currentMediaUrl}
                            controls
                            className = "h-32 object-contain rounded"
                        />
                    )}

                    {currentMediaType === 'audio' && (
                        <audio
                            src = {currentMediaUrl}
                            controls
                            className = "w-full mt-2"
                        />
                    )}

                    <button
                        type = 'button'
                        onClick = {onRemove}
                        className = "mt-4 bg-btn-wrong text-ink font-bold font-mono text-lg px-4 py-2 border-4 border-ink shadow-brutal-sm hover:-translate-y-1 active:translate-y-1 active:shadow-none transition-all uppercase"
                        disabled = {localLoading}
                    >
                        Remove Media
                    </button>
                </div>
            )}
        </div>

    )

}