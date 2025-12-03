import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { McpService } from '../../services/mcp.service';
import { UserProfile } from '../../models';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginForm: FormGroup;
  loading = false;
  error: string | null = null;
  isNewUser = false; // Toggle between existing user and new user flow
  checkingUser = false;

  hobbiesOptions = ['Reading', 'Gaming', 'Sports', 'Music', 'Art', 'Coding', 'Cooking'];
  interestsOptions = ['Technology', 'Science', 'Finance', 'History', 'Nature', 'Space', 'Animals'];

  constructor(
    private fb: FormBuilder,
    private mcpService: McpService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      age: [10, [Validators.required, Validators.min(6), Validators.max(18)]],
      hobbies: [[]],
      interests: [[]]
    });
  }

  toggleHobby(hobby: string) {
    const hobbies = this.loginForm.get('hobbies')?.value || [];
    const index = hobbies.indexOf(hobby);
    if (index > -1) {
      hobbies.splice(index, 1);
    } else {
      hobbies.push(hobby);
    }
    this.loginForm.patchValue({ hobbies });
  }

  toggleInterest(interest: string) {
    const interests = this.loginForm.get('interests')?.value || [];
    const index = interests.indexOf(interest);
    if (index > -1) {
      interests.splice(index, 1);
    } else {
      interests.push(interest);
    }
    this.loginForm.patchValue({ interests });
  }

  isHobbySelected(hobby: string): boolean {
    const hobbies = this.loginForm.get('hobbies')?.value || [];
    return hobbies.includes(hobby);
  }

  isInterestSelected(interest: string): boolean {
    const interests = this.loginForm.get('interests')?.value || [];
    return interests.includes(interest);
  }

  async checkExistingUser() {
    const name = this.loginForm.get('name')?.value;
    
    if (!name || name.length < 2) {
      this.error = 'Please enter a valid name';
      return;
    }

    this.checkingUser = true;
    this.error = null;

    try {
      const response: any = await this.mcpService.loginUser(name).toPromise();
      
      if (response.is_existing) {
        // Existing user - log them in
        const user = response.user;
        this.mcpService.setCurrentUser(user);
        
        // Load gamification data
        await this.mcpService.getGamificationData(user.user_id).toPromise();
        
        this.router.navigate(['/dashboard']);
      } else {
        // New user - show onboarding form
        this.isNewUser = true;
      }
    } catch (err: any) {
      this.error = err.message || 'Failed to check user. Please try again.';
    } finally {
      this.checkingUser = false;
    }
  }

  async onSubmit() {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = null;

    try {
      const formValue = this.loginForm.value;
      const userId = `user_${Date.now()}`;
      
      const profile: UserProfile = {
        user_id: userId,
        name: formValue.name,
        age: formValue.age,
        hobbies: formValue.hobbies || [],
        interests: formValue.interests || []
      };

      await this.mcpService.createUserProfile(profile).toPromise();
      
      // Load gamification data
      await this.mcpService.getGamificationData(userId).toPromise();
      
      this.router.navigate(['/dashboard']);
    } catch (err: any) {
      this.error = err.message || 'Failed to create profile. Please try again.';
    } finally {
      this.loading = false;
    }
  }

  toggleToNewUser() {
    this.isNewUser = true;
    this.error = null;
  }

  backToLogin() {
    this.isNewUser = false;
    this.loginForm.reset({ name: this.loginForm.get('name')?.value, age: 10, hobbies: [], interests: [] });
    this.error = null;
  }
}
