"use client"

import type React from "react"

import { useState } from "react"
import Image from "next/image"
import { Upload, Download, Sliders, RotateCcw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"

// API URL constants
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ColorizePage() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [colorizedImage, setColorizedImage] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [imageId, setImageId] = useState<string | null>(null)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string)
        setColorizedImage(null)
        setImageId(null)
        setError(null)
      }
      reader.readAsDataURL(file)
    }
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
      formData.append('title', 'Image from Web App');
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

  const resetProcess = () => {
    setColorizedImage(null);
    setImageId(null);
    setError(null);
  }

  return (
    <div className="container py-10">
      <div className="flex flex-col space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-green-900 mb-2">Image Colorization</h1>
          <p className="text-gray-600">Upload a black and white photo to colorize with our AI technology</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <Card className="col-span-1">
            <CardContent className="p-6">
              <div className="flex flex-col space-y-4">
                <h2 className="text-xl font-semibold text-green-800">Upload Image</h2>
                <div
                  className="border-2 border-dashed border-green-200 rounded-lg p-8 flex flex-col items-center justify-center bg-green-50/50 cursor-pointer hover:bg-green-50 transition-colors"
                  onClick={() => document.getElementById("image-upload")?.click()}
                >
                  <input
                    id="image-upload"
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleImageUpload}
                  />
                  <Upload className="h-10 w-10 text-green-700 mb-4" />
                  <p className="text-sm text-gray-600 mb-2 text-center">
                    Drag and drop your image here or click to browse
                  </p>
                  <p className="text-xs text-gray-500 text-center">Supports JPG, PNG (Max 10MB)</p>
                </div>

                <Separator className="my-4" />

                <div className="space-y-4">
                  <h3 className="font-medium text-green-800">Image Settings</h3>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <label className="text-sm text-gray-600">Colorization Intensity</label>
                      <span className="text-sm text-gray-600">75%</span>
                    </div>
                    <Slider defaultValue={[75]} max={100} step={1} />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <label className="text-sm text-gray-600">Historical Accuracy</label>
                      <span className="text-sm text-gray-600">90%</span>
                    </div>
                    <Slider defaultValue={[90]} max={100} step={1} />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <label className="text-sm text-gray-600">Detail Enhancement</label>
                      <span className="text-sm text-gray-600">60%</span>
                    </div>
                    <Slider defaultValue={[60]} max={100} step={1} />
                  </div>
                </div>

                <Button
                  className="w-full bg-green-700 hover:bg-green-800 text-white mt-4"
                  disabled={!selectedImage || isProcessing}
                  onClick={processImage}
                >
                  {isProcessing ? "Processing..." : "Colorize Image"}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="col-span-1 lg:col-span-2">
            <CardContent className="p-6">
              <Tabs defaultValue="preview" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-green-50">
                  <TabsTrigger
                    value="preview"
                    className="data-[state=active]:bg-green-100 data-[state=active]:text-green-900"
                  >
                    Preview
                  </TabsTrigger>
                  <TabsTrigger
                    value="comparison"
                    className="data-[state=active]:bg-green-100 data-[state=active]:text-green-900"
                  >
                    Comparison
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="preview" className="mt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col">
                      <h3 className="text-sm font-medium text-green-800 mb-2">Original</h3>
                      <div className="aspect-square relative bg-gray-100 rounded-md overflow-hidden border border-gray-200">
                        {selectedImage ? (
                          <Image
                            src={selectedImage || "/placeholder.svg"}
                            alt="Original black and white image"
                            fill
                            className="object-contain"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                            No image selected
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col">
                      <h3 className="text-sm font-medium text-green-800 mb-2">Colorized</h3>
                      <div className="aspect-square relative bg-gray-100 rounded-md overflow-hidden border border-gray-200">
                        {colorizedImage ? (
                          <Image
                            src={colorizedImage || "/placeholder.svg"}
                            alt="Colorized image"
                            fill
                            className="object-contain"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                            {isProcessing ? "Processing..." : "Awaiting colorization"}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {colorizedImage && (
                    <div className="flex justify-end gap-2 mt-4">
                      <Button 
                        variant="outline" 
                        className="border-green-700 text-green-700 hover:bg-green-50"
                        onClick={resetProcess}
                      >
                        <RotateCcw className="mr-2 h-4 w-4" />
                        Reset
                      </Button>
                      <Button 
                        className="bg-green-700 hover:bg-green-800 text-white"
                        onClick={downloadImage}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Download
                      </Button>
                    </div>
                  )}

                  {error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                      {error}
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="comparison" className="mt-4">
                  <div className="relative aspect-[16/9] bg-gray-100 rounded-md overflow-hidden border border-gray-200">
                    {selectedImage && colorizedImage ? (
                      <div className="relative h-full w-full">
                        <Image
                          src={selectedImage || "/placeholder.svg"}
                          alt="Original black and white image"
                          fill
                          className="object-contain"
                        />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="bg-white/80 px-4 py-2 rounded-full text-sm font-medium text-green-800">
                            Drag slider to compare
                          </div>
                        </div>
                        <div className="absolute inset-y-0 left-0 w-1/2 overflow-hidden border-r-2 border-green-500">
                          <Image
                            src={colorizedImage || "/placeholder.svg"}
                            alt="Colorized image"
                            fill
                            className="object-contain object-left"
                          />
                        </div>
                        <div className="absolute inset-y-0 left-1/2 w-1 bg-green-500 -ml-0.5 cursor-ew-resize" />
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                        {isProcessing ? "Processing..." : "Awaiting colorization"}
                      </div>
                    )}
                  </div>

                  {colorizedImage && (
                    <div className="flex justify-end gap-2 mt-4">
                      <Button 
                        className="bg-green-700 hover:bg-green-800 text-white"
                        onClick={downloadImage}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Download
                      </Button>
                    </div>
                  )}

                  {error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                      {error}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

