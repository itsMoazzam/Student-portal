'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/utils/api'; // Adjust the path as needed
import '../../login/styles.css';
import { AxiosError } from 'axios';
import { FaEye, FaEyeSlash } from 'react-icons/fa';

const CreateStudentPage = () => {
    const router = useRouter();

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
    });

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleSubmit = async () => {
        if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
            setError('All fields are required');
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        try {
            await api.post('/students/create/', {
                username: formData.username,
                email: formData.email,
                password: formData.password,
            });

            setSuccess('Student created successfully');
            setFormData({
                username: '',
                email: '',
                password: '',
                confirmPassword: '',
            });

            setTimeout(() => {
                setSuccess('');
                router.push('/admin/students');
            }, 1500);
        } catch (err: unknown) {
            if (err instanceof AxiosError) {
                setError(err.response?.data?.detail || 'Failed to create student');
            } else {
                setError('Something went wrong');
            }

            setTimeout(() => setError(''), 3000);
        }
    };


    return (
        <div className="glass-container">
            <div className="glass-form">
                <h2 className="glass-heading">Create New Student</h2>

                <div className="input-group">
                    <input
                        type="text"
                        name="username"
                        placeholder="Username"
                        className="glass-input"
                        value={formData.username}
                        onChange={handleChange}
                    />
                </div>

                <div className="input-group">
                    <input
                        type="email"
                        name="email"
                        placeholder="Email"
                        className="glass-input"
                        value={formData.email}
                        onChange={handleChange}
                    />
                </div>

                <div className="input-group">
                    <input
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        placeholder="Password"
                        className="glass-input"
                        value={formData.password}
                        onChange={handleChange}
                    />
                    <button
                        className="password-toggle"
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                    >
                        {showPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                </div>

                <div className="input-group">
                    <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        name="confirmPassword"
                        placeholder="Confirm Password"
                        className="glass-input"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                    />
                    <button
                        className="password-toggle"
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                        {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                </div>

                <button className="glass-btn" onClick={handleSubmit}>
                    Create Student
                </button>

                {error && <pre className="glass-error">{error}</pre>}
                {success && <pre className="glass-success">{success}</pre>}
            </div>
        </div>
    );
};

export default CreateStudentPage;
