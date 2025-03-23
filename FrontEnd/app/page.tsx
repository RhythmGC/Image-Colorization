"use client"

import type React from "react"

import { useState } from "react"
import Image from "next/image"
import { Upload } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// API URL constants
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function HomePage() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [colorizedImage, setColorizedImage] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [imageId, setImageId] = useState<string | null>(null)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setIsUploading(true)
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string)
        setColorizedImage(null)
        setImageId(null)
        setError(null)
        setIsUploading(false)
      }
      reader.readAsDataURL(file)
    }
  }

  const triggerFileInput = () => {
    document.getElementById("image-upload")?.click()
  }

  const processImage = async () => {
    if (!selectedImage) return
    
    setIsProcessing(true)
    setError(null)
    
    try {
      // Convert base64 string to file object
      const base64Response = await fetch(selectedImage);
      const blob = await base64Response.blob();
      
      const formData = new FormData();
      formData.append('file', blob, 'image.jpg');
      formData.append('title', 'Image from Home Page');
      formData.append('auto_colorize', 'true');
      
      // Upload the image and get colorized version in one step
      const response = await fetch(`${API_URL}/upload-image`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.colorized && data.colorized_cloudinary_url) {
        setColorizedImage(data.colorized_cloudinary_url);
        setImageId(data._id);
      } else if (data.cloudinary_url) {
        // If auto-colorize failed but we have the original image
        setImageId(data._id);
        
        // Try to colorize separately
        const colorizeResponse = await fetch(`${API_URL}/images/${data._id}/colorize`, {
          method: 'POST',
        });
        
        if (colorizeResponse.ok) {
          const colorizeData = await colorizeResponse.json();
          if (colorizeData.colorized_cloudinary_url) {
            setColorizedImage(colorizeData.colorized_cloudinary_url);
          }
        }
      }
    } catch (err) {
      console.error('Error processing image:', err);
      setError(err instanceof Error ? err.message : 'Failed to process image');
    } finally {
      setIsProcessing(false);
    }
  }

  const downloadImage = () => {
    if (colorizedImage) {
      window.open(colorizedImage, '_blank');
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 bg-white">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl text-green-900">
                  Colorize Your Historical Photos
                </h2>
                <p className="max-w-[900px] text-gray-600 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Our advanced AI technology specializes in colorizing photos of Vietnamese soldiers with historical
                  accuracy, preserving the authentic details of uniforms, medals, and environments.
                </p>
              </div>
            </div>

            <div className="mx-auto max-w-3xl mt-12">
              <Tabs defaultValue="upload" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-green-50">
                  <TabsTrigger
                    value="upload"
                    className="data-[state=active]:bg-green-100 data-[state=active]:text-green-900"
                  >
                    Upload
                  </TabsTrigger>
                  <TabsTrigger
                    value="process"
                    className="data-[state=active]:bg-green-100 data-[state=active]:text-green-900"
                  >
                    Process
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="upload" className="p-6 border rounded-b-lg border-green-100">
                  <div className="flex flex-col items-center gap-4">
                    <input
                      id="image-upload"
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handleImageUpload}
                    />
                    <div
                      className="border-2 border-dashed border-green-200 rounded-lg p-12 w-full flex flex-col items-center justify-center bg-green-50/50 cursor-pointer hover:bg-green-50 transition-colors"
                      onClick={triggerFileInput}
                    >
                      {selectedImage ? (
                        <div className="relative w-full aspect-video">
                          <Image
                            src={selectedImage || "/placeholder.svg"}
                            alt="Selected image"
                            fill
                            className="object-contain"
                          />
                        </div>
                      ) : (
                        <>
                          <Upload className="h-12 w-12 text-green-700 mb-4" />
                          <p className="text-sm text-gray-600 mb-2">Drag and drop your image here or click to browse</p>
                          <p className="text-xs text-gray-500">Supports JPG, PNG (Max 10MB)</p>
                        </>
                      )}
                    </div>
                    <div className="flex flex-row gap-4 w-full justify-center">
                      <Button
                        className="bg-green-700 hover:bg-green-800 text-white"
                        onClick={triggerFileInput}
                        disabled={isUploading}
                      >
                        {isUploading ? "Uploading..." : selectedImage ? "Change Image" : "Upload Image"}
                      </Button>
                      {selectedImage && (
                        <Button
                          className="bg-green-700 hover:bg-green-800 text-white"
                          onClick={() => {
                            const processTab = document.querySelector('[data-value="process"]') as HTMLElement;
                            processTab?.click();
                            processImage();
                          }}
                          disabled={isProcessing}
                        >
                          {isProcessing ? "Processing..." : "Continue to Process"}
                        </Button>
                      )}
                    </div>
                    {error && (
                      <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm w-full">
                        {error}
                      </div>
                    )}
                  </div>
                </TabsContent>
                <TabsContent value="process" className="p-6 border rounded-b-lg border-green-100">
                  <div className="flex flex-col items-center gap-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                      <div className="aspect-square relative bg-gray-100 rounded-md overflow-hidden">
                        {selectedImage ? (
                          <Image
                            src={selectedImage || "/placeholder.svg"}
                            alt="Original black and white image"
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                            No image selected
                          </div>
                        )}
                        <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-2">
                          Original
                        </div>
                      </div>
                      <div className="aspect-square relative bg-gray-100 rounded-md overflow-hidden">
                        {isProcessing ? (
                          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                            Processing...
                          </div>
                        ) : colorizedImage ? (
                          <Image
                            src={colorizedImage}
                            alt="Colorized image"
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                            {selectedImage ? "Click 'Process' to colorize" : "No image selected"}
                          </div>
                        )}
                        <div className="absolute bottom-0 left-0 right-0 bg-green-700/60 text-white text-xs p-2">
                          Colorized
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-4">
                      <Button 
                        className="bg-green-700 hover:bg-green-800 text-white" 
                        disabled={!colorizedImage}
                        onClick={downloadImage}
                      >
                        Download
                      </Button>
                      {!colorizedImage && selectedImage && !isProcessing && (
                        <Button
                          className="bg-green-700 hover:bg-green-800 text-white"
                          onClick={processImage}
                        >
                          Process
                        </Button>
                      )}
                    </div>
                    {error && (
                      <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm w-full">
                        {error}
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

