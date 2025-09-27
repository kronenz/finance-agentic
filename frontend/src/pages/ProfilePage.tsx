import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

const ProfilePage: React.FC = () => {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Profile</h1>

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>Update your personal details here.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6 max-w-lg">
            <div className="space-y-1">
              <label htmlFor="name" className="text-sm font-medium">Full Name</label>
              <Input id="name" type="text" defaultValue="John Doe" />
            </div>
            <div className="space-y-1">
              <label htmlFor="email" className="text-sm font-medium">Email Address</label>
              <Input id="email" type="email" defaultValue="john.doe@example.com" />
            </div>
            <div>
              <Button type="submit">Save Changes</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Update your password here for security.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6 max-w-lg">
            <div className="space-y-1">
              <label htmlFor="current-password">Current Password</label>
              <Input id="current-password" type="password" />
            </div>
            <div className="space-y-1">
              <label htmlFor="new-password">New Password</label>
              <Input id="new-password" type="password" />
            </div>
            <div className="space-y-1">
              <label htmlFor="confirm-password">Confirm New Password</label>
              <Input id="confirm-password" type="password" />
            </div>
            <div>
              <Button type="submit">Update Password</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfilePage;