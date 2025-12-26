import React from 'react'
import { Sidebar } from './Sidebar'

interface LayoutProps {
    children: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className="flex min-h-screen bg-[#0a0a0b] text-white">
            <Sidebar />
            <main className="flex-1 ml-64 p-8">
                <div className="max-w-6xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    )
}
